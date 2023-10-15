#!/usr/bin/env python3

import sys
import time
import traceback
from datetime import timedelta
from lib.timestamp import epoch_now
from decimal import Decimal

from db import SwapDB
from lib import wallets, utils
import exchange
from lib.logger import Logger

# XXX TODO
#  ? Send Lock
#  Eventually expire active tx that cant send or refund


class MimExchange:
    def __init__(self):
        self.db = SwapDB()
        self.logger = Logger(log_level="INFO")

    def run(self):
        try:
            exit_handler = utils.ExitHandler()
            self.logger.warning("MIME Started")
            while not exit_handler.do_exit:
                # Read config from DB
                config = SwapDB().get_config()
                if config is None:
                    self.logger.error("Config not found in database, please create it")
                    sys.exit(1)
                expire_afer = timedelta(days=int(config["incomplete_swap_expire"])).total_seconds()
                archive_after = timedelta(days=int(config["completed_swap_archive"])).total_seconds()
                delete_after = timedelta(days=int(config["archived_swap_delete"])).total_seconds()

                ##
                # Get and process each active swap
                active = list(self.db.get_active_swaps().keys())
                self.logger.info(f"Processing {len(active)} active swaps: {active}")

                for id in active:
                    try:
                        self.logger.info(f"Processing: {id}")

                        ##
                        # Incomplete and Expired
                        swap = self.db.get_swap(id)
                        expire_ts = swap.ts + expire_afer
                        if expire_ts < epoch_now() and swap.recvd_from is False:
                            # Delete this incompleted and expired swap
                            self.logger.info(f"Delete expired incomplete swap: {swap.id}")
                            self.db.del_swap(swap.id)
                            continue  # Do not process deleted swap

                        ##
                        # Payment not Received
                        swap = self.db.get_swap(id)
                        if swap.recvd_from == False:
                            recv_tx_list = wallets.get_recv_tx_list(swap.swap_from, swap.send_from_address)
                            if len(recv_tx_list) > 0:
                                exchange_tx_amount = wallets.get_recv_tx(swap.swap_from, recv_tx_list[0])["amount"]
                                self.logger.info(f"Received {exchange_tx_amount} {swap.swap_from} for: {swap.id}")
                                swap.recvd_from = True
                                swap.swap_from_amount = exchange_tx_amount
                                self.db.set_swap(swap)

                        ##
                        # Payment Received but Exchange not calculated
                        swap = self.db.get_swap(id)
                        if swap.recvd_from == True and swap.swap_executed_ts is None:
                            # Calculate the exchange - This locks the rate
                            self.logger.info(f"Calculating exchange for: {swap.id}")
                            swap.swap_executed_ts = epoch_now()
                            exchange.calculate_swap(swap)
                            self.db.set_swap(swap)

                        ##
                        # Exchange calculated but not sent or refunded
                        swap = self.db.get_swap(id)
                        if swap.swap_executed_ts is not None and swap.sent_to_txid is None and swap.refund_txid is None:
                            # Send Exchange
                            self.logger.warning(f"Sending: {swap.swap_to_amount} {swap.swap_to} for {swap.id}")
                            with utils.DeferSignals():
                                try:
                                    self.db.ping()
                                    txid = wallets.send(swap.swap_to, swap.swap_to_amount, swap.swap_to_address)
                                    swap.sent_to_txid = txid
                                    swap.send_failed = False
                                    self.db.set_swap(swap)
                                except wallets.WalletEx as e:
                                    # Send Failed in a way we can handle
                                    swap.send_failed = True
                                    self.db.set_swap(swap)
                                    self.logger.error(f"Swap {swap.id} failed to send {swap.swap_to_amount} {swap.swap_to} - {str(e)}")

                        ##
                        # Exchange sent but not confirmed
                        swap = self.db.get_swap(id)
                        if swap.sent_to_txid is not None and swap.sent_to_confirmed == False:
                            # Check for send tx confirmation
                            self.logger.info(f"Checking for send confirmation for: {swap.id}")
                            confirmed = wallets.send_tx_confirmed(swap.swap_to, swap.sent_to_txid)
                            if confirmed == True:
                                swap.sent_to_confirmed = True
                                self.db.set_swap(swap)
                                self.logger.info(f"Send confirmed for: {swap.id}")

                        ##
                        # Exchange send tx confirmed - swap complete
                        swap = self.db.get_swap(id)
                        if swap.sent_to_confirmed == True:
                            self.logger.info("Swap Complete: {}".format(swap.dict()))
                            self.db.complete_swap(swap.id)
                            continue

                        
                        ##
                        # Error Sending
                        swap = self.db.get_swap(id)
                        # Get refund amount
                        refund_amount = swap.swap_from_amount
                        swap = self.db.get_swap(id)
                        if swap.send_failed == True:
                            ##
                            # No refund address provided
                            if swap.refund_address is None:
                                self.logger.info(f"No refund address is provided for: {swap.id}")
                                continue

                            ##
                            # Refund address provided but exchange is not sent and refund not sent
                            swap = self.db.get_swap(id)
                            if swap.refund_txid is None and swap.sent_to_txid is None:
                                # Send Refund
                                self.logger.warning(f"Sending Refund: {refund_amount} {swap.swap_from} for {swap.id}")
                                with utils.DeferSignals():
                                    try:
                                        self.db.ping()
                                        txid = wallets.send(swap.swap_from, refund_amount, swap.refund_address)
                                        swap.refund_txid = txid
                                        self.db.set_swap(swap)
                                    except wallets.WalletEx as e:
                                        # Send Failed.  We dont set any flags because there is nothing else to do except try again later
                                        self.logger.error(f"Swap {swap.id} failed to send refund {refund_amount} {swap.swap_from} - {str(e)}")

                            ##
                            # Refund sent but not confirmed
                            swap = self.db.get_swap(id)
                            if swap.refund_txid is not None and swap.refund_confirmed == False:
                                self.logger.info(f"Checking for refund send confirmation for: {swap.id}")
                                confirmed = wallets.send_tx_confirmed(swap.swap_from, swap.refund_txid)
                                if confirmed == True:
                                    swap.refund_confirmed = True
                                    self.db.set_swap(swap)
                                    self.logger.info(f"Refund send confirmed for: {swap.id}")

                            ##
                            # Refund Confirmed - swap completed
                            swap = self.db.get_swap(id)
                            if swap.refund_confirmed == True:
                                self.logger.info("Swap Complete: {}".format(swap.dict()))
                                self.db.complete_swap(swap.id)
                                continue

                    except Exception as e:
                        self.logger.error(f"Failed to process active swap {swap.id}: {str(e)}")


                ##
                # Process completed swaps
                completed = list(self.db.get_completed_swaps().keys())
                self.logger.info(f"Processing {len(completed)} completed swaps: {completed}")

                for id in completed:
                    try:
                        self.logger.info(f"Processing completed swap: {id}")
                        
                        ##
                        # Check for extra recv tx
                        swap = self.db.get_swap(id)
                        extra_recv_txs = wallets.get_recv_tx_list(swap.swap_from, swap.send_from_address)[1:]
                        num_refunded_extra_txs = len(swap.extra_refund_txids)
                        unrefunded_extra_recv_txs = extra_recv_txs[num_refunded_extra_txs:]
                        # Record the fact of extra recvs - for the UI
                        if len(extra_recv_txs) > 0 and swap.extra_recvs == False:
                            swap.extra_recvs = True
                            self.db.set_completed_swap(swap)  # This is set for the UI
                        # Record amounts of extra recvs - for the UI
                        if len(extra_recv_txs) > len(swap.extra_recv_txs):
                            extra_recv_tx_data = []
                            for tx in extra_recv_txs:
                                tx_data = wallets.get_recv_tx(swap.swap_from, tx)
                                extra_recv_tx_data.append((str(tx_data["amount"]), tx,))  # list of tuple
                                swap.extra_recv_txs = extra_recv_tx_data
                            self.db.set_completed_swap(swap)

                        ##
                        # Refund the next extra recv tx
                        if len(unrefunded_extra_recv_txs) > 0:
                            refund_tx = unrefunded_extra_recv_txs[0]
                            if swap.refund_address is None:
                                self.logger.info(f"Extra Recv TX but no refund address for: {swap.id}")
                                continue
                            refund_tx_data = wallets.get_recv_tx(swap.swap_from, refund_tx)
                            # Get refund amount
                            refund_amount = refund_tx_data["amount"]
                            ##
                            # Send extra tx refund
                            self.logger.warning(f"Sending Extra TX Refund: {refund_amount} {swap.swap_from} for {swap.id}")
                            with utils.DeferSignals():
                                try:
                                    self.db.ping()
                                    txid = wallets.send(swap.swap_from, refund_amount, swap.refund_address)
                                    swap.extra_refund_txids.append(txid)
                                    self.db.set_completed_swap(swap)
                                except wallets.WalletEx as e:
                                    # Refund extra Send Failed.  We dont set any flags because there is nothing else to do except try again later
                                    self.logger.error(f"Swap {swap.id} failed to send extra tx refund {refund_amount} {swap.swap_from} - {str(e)}")
                                    if refund_amount < Decimal(self.db.get_tx_fees()[swap.swap_from]):
                                        self.logger.error(f"Swap {swap.id} extra tx refund {refund_amount} {swap.swap_from} is too small")
                                        swap.extra_refund_txids.append("Amounts less than network transaction fee can not be refunded")
                                        self.db.set_completed_swap(swap)
                        ##
                        # Check if its old enough to archive
                        swap = self.db.get_swap(id)
                        archive_ts = swap.ts + archive_after
                        if archive_ts < epoch_now():
                            self.logger.info("Cleaning up old swap record: {}".format(swap.dict()))
                            self.db.archive_swap(id)

                    except Exception as e:
                        self.logger.error(f"Failed to process completed swap {swap.id}: {str(e)}")

                ##
                # Process archived swaps
                archived = list(self.db.get_archived_swaps().keys())
                self.logger.info(f"Processing {len(archived)} archived swaps")
                for id in archived:
                    swap = self.db.get_swap(id)
                    delete_ts = swap.ts + delete_after
                    if delete_ts < epoch_now():
                        self.db.del_swap(id)


                ##
                # Set exchange heartbeat timestamp
                self.db.set_exchange_heartbeat(epoch_now())

                ##
                # Delay between loops but process signals every second
                for _ in range(30):
                    if not exit_handler.do_exit:
                        time.sleep(1)

        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error("ERROR: {} - {}".format(str(e), tb))
            time.sleep(60)



if __name__ == "__main__":
   mime = MimExchange()
   mime.run()

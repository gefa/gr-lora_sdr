#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lora Rx
# GNU Radio version: 3.8.1.0

from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import lora_sdr


class lora_RX(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Lora Rx")

        ##################################################
        # Variables
        ##################################################
        self.sf = sf = 7
        self.samp_rate = samp_rate = 125000
        self.pay_len = pay_len = 64
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.cr = cr = 4
        self.bw = bw = 125000

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(('', "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_center_freq(915e6, 0)
        self.uhd_usrp_source_0.set_rx_agc(True, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0.set_bandwidth(bw, 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec())
        self.lora_sdr_header_decoder_0 = lora_sdr.header_decoder(impl_head, cr, pay_len, has_crc)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec()
        self.lora_sdr_gray_enc_0 = lora_sdr.gray_enc()
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(samp_rate, bw, sf, impl_head)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod(samp_rate, bw, sf, impl_head)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver(sf)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif(True)
        self.interp_fir_filter_xxx_0 = filter.interp_fir_filter_ccf(4, [-0.128616616593872,	-0.212206590789194,	-0.180063263231421,	3.89817183251938e-17	,0.300105438719035	,0.636619772367581	,0.900316316157106,	1	,0.900316316157106,	0.636619772367581,	0.300105438719035,	3.89817183251938e-17,	-0.180063263231421,	-0.212206590789194,	-0.128616616593872])
        self.interp_fir_filter_xxx_0.declare_sample_delay(0)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_sdr_frame_sync_0, 'new_frame'), (self.lora_sdr_deinterleaver_0, 'new_frame'))
        self.msg_connect((self.lora_sdr_frame_sync_0, 'new_frame'), (self.lora_sdr_dewhitening_0, 'new_frame'))
        self.msg_connect((self.lora_sdr_frame_sync_0, 'new_frame'), (self.lora_sdr_fft_demod_0, 'new_frame'))
        self.msg_connect((self.lora_sdr_frame_sync_0, 'new_frame'), (self.lora_sdr_hamming_dec_0, 'new_frame'))
        self.msg_connect((self.lora_sdr_frame_sync_0, 'new_frame'), (self.lora_sdr_header_decoder_0, 'new_frame'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_crc_verif_0, 'CRC'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'pay_len'), (self.lora_sdr_crc_verif_0, 'pay_len'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_deinterleaver_0, 'CR'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'pay_len'), (self.lora_sdr_dewhitening_0, 'pay_len'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_dewhitening_0, 'CRC'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_fft_demod_0, 'CR'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_frame_sync_0, 'CR'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'err'), (self.lora_sdr_frame_sync_0, 'err'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'CRC'), (self.lora_sdr_frame_sync_0, 'crc'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'pay_len'), (self.lora_sdr_frame_sync_0, 'pay_len'))
        self.msg_connect((self.lora_sdr_header_decoder_0, 'CR'), (self.lora_sdr_hamming_dec_0, 'CR'))
        self.connect((self.interp_fir_filter_xxx_0, 0), (self.lora_sdr_frame_sync_0, 0))
        self.connect((self.lora_sdr_deinterleaver_0, 0), (self.lora_sdr_hamming_dec_0, 0))
        self.connect((self.lora_sdr_dewhitening_0, 0), (self.lora_sdr_crc_verif_0, 0))
        self.connect((self.lora_sdr_fft_demod_0, 0), (self.lora_sdr_gray_enc_0, 0))
        self.connect((self.lora_sdr_frame_sync_0, 0), (self.lora_sdr_fft_demod_0, 0))
        self.connect((self.lora_sdr_gray_enc_0, 0), (self.lora_sdr_deinterleaver_0, 0))
        self.connect((self.lora_sdr_hamming_dec_0, 0), (self.lora_sdr_header_decoder_0, 0))
        self.connect((self.lora_sdr_header_decoder_0, 0), (self.lora_sdr_dewhitening_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.interp_fir_filter_xxx_0, 0))


    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_pay_len(self):
        return self.pay_len

    def set_pay_len(self, pay_len):
        self.pay_len = pay_len

    def get_impl_head(self):
        return self.impl_head

    def set_impl_head(self, impl_head):
        self.impl_head = impl_head

    def get_has_crc(self):
        return self.has_crc

    def set_has_crc(self, has_crc):
        self.has_crc = has_crc

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.uhd_usrp_source_0.set_bandwidth(self.bw, 0)
        self.uhd_usrp_source_0.set_bandwidth(self.bw, 1)





def main(top_block_cls=lora_RX, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()

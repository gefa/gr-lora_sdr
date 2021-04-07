#include "dewhitening_impl.h"
#include "tables.h"
#include <gnuradio/io_signature.h>
// Fix for libboost > 1.75
#include <boost/bind/placeholders.hpp>

using namespace boost::placeholders;
namespace gr {
namespace lora_sdr {

dewhitening::sptr dewhitening::make() {
  return gnuradio::get_initial_sptr(new dewhitening_impl());
}

/**
 * @brief Construct a new dewhitening impl object
 *
 */
dewhitening_impl::dewhitening_impl()
    : gr::block("dewhitening", gr::io_signature::make(1, 1, sizeof(uint8_t)),
                gr::io_signature::make(1, 1, sizeof(uint8_t))) {
  message_port_register_in(pmt::mp("pay_len"));
  set_msg_handler(
      pmt::mp("pay_len"),
      boost::bind(&dewhitening_impl::header_pay_len_handler, this, _1));
  message_port_register_in(pmt::mp("new_frame"));
  set_msg_handler(pmt::mp("new_frame"),
                  boost::bind(&dewhitening_impl::new_frame_handler, this, _1));
  message_port_register_in(pmt::mp("CRC"));
  set_msg_handler(pmt::mp("CRC"),
                  boost::bind(&dewhitening_impl::header_crc_handler, this, _1));
  set_tag_propagation_policy(TPP_ALL_TO_ALL);
}

/**
 * @brief Destroy the dewhitening impl object
 *
 */
dewhitening_impl::~dewhitening_impl() {}

/**
 * @brief standard gnuradio function to tell the system when to start work
 *
 * @param noutput_items : number of output items
 * @param ninput_items_required : number of input items required
 */
void dewhitening_impl::forecast(int noutput_items,
                                gr_vector_int &ninput_items_required) {
  ninput_items_required[0] = 2;
}

/**
 * @brief Handles the payload length received from the header_decoder block.
 *
 * @param payload_len : payload length
 */
void dewhitening_impl::header_pay_len_handler(pmt::pmt_t payload_len) {
  m_payload_len = pmt::to_long(payload_len);
};

/**
 * @brief Reset the block variables for a new frame.
 *
 * @param id
 */
void dewhitening_impl::new_frame_handler(pmt::pmt_t id) { offset = 0; }

/**
 * @brief Receive indication on the CRC presence
 *
 * @param crc_presence : control message if add_crc is active
 */
void dewhitening_impl::header_crc_handler(pmt::pmt_t crc_presence) {
  m_crc_presence = pmt::to_long(crc_presence);
};

/**
 * @brief Main dewhitining function
 *
 * @param noutput_items : number of output items
 * @param ninput_items : number of input items
 * @param input_items : input data (i.e. header_decoder stage)
 * @param output_items : output data
 * @return int
 */
int dewhitening_impl::general_work(int noutput_items,
                                   gr_vector_int &ninput_items,
                                   gr_vector_const_void_star &input_items,
                                   gr_vector_void_star &output_items) {
  const uint8_t *in = (const uint8_t *)input_items[0];
  uint8_t *out = (uint8_t *)output_items[0];

  std::vector<tag_t> return_tag;
  get_tags_in_range(return_tag, 0, 0, nitems_read(0) + 100000);
  // if (return_tag.size() > 0) {
  //   // std::cout << "DEwhit Sync Done" << std::endl;
  //   add_item_tag(0, nitems_written(0), pmt::intern("status"),
  //                pmt::intern("done"));
  //   consume_each(ninput_items[0]);
  //   return 1;
  // }

  uint8_t low_nib, high_nib;
  for (int i = 0; i < ninput_items[0] / 2; i++) {

    if (offset < m_payload_len) {
      low_nib = in[2 * i] ^ (whitening_seq[offset] & 0x0F);
      high_nib = in[2 * i + 1] ^ (whitening_seq[offset] & 0xF0) >> 4;
      dewhitened.push_back(high_nib << 4 | low_nib);
    } else if ((offset < m_payload_len + 2) &&
               m_crc_presence) { // do not dewhiten the CRC
      low_nib = in[2 * i];
      high_nib = in[2 * i + 1];
      dewhitened.push_back(high_nib << 4 | low_nib);
    } else { // full packet received
      break;
    }
    offset++;
  }
#ifdef GRLORA_DEBUG
// for (uint i=0 ; i<dewhitened.size() ; i++){
//     std::cout<<(char)(int)dewhitened[i]<<"    0x"<< std::hex <<
//     (int)dewhitened[i]<<std::dec<<std::endl;
// }
#endif
  consume_each(dewhitened.size() * 2); // ninput_items[0]/2*2);
  noutput_items = dewhitened.size();
  memcpy(out, &dewhitened[0], noutput_items * sizeof(uint8_t));

  dewhitened.clear();
  return noutput_items;
}
} // namespace lora_sdr
} /* namespace gr */

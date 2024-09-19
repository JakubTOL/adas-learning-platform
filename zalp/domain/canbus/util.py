def is_not_sent_by(dut_name, msg):
    return dut_name not in msg.senders

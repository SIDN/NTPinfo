class NtpTimestamp:
    def __init__(self, client_sent_time,server_recv_time,server_sent_time,client_recv_time):
        self.client_sent_time = client_sent_time
        self.server_recv_time = server_recv_time
        self.server_sent_time = server_sent_time
        self.client_recv_time = client_recv_time
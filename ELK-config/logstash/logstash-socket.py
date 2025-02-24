
import sys
import socket
import json
import argparse
import logging


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)



class SOCKET_JSON:
    """
    UDP SOCKET with Logstsh
    """

    socket_logstash_dict = {}

    def socket_json_push(self, key, value):
         if key not in self.socket_logstash_dict.keys():
            self.socket_logstash_dict[key] = value
            # self.socket_logstash_dict[key].append(value)
            # del (self.socket_logstash_dict[key][0])


    def get_socket_json_pop(self):
        return self.socket_logstash_dict


class TCP_SOCKET:
    """
    TCP SOCKET with Logstsh
    """
    def __init__(self, ip, port):
        self.target_server_ip = ip
        self.socket_port = port


    def socket_logstash_handler(self, message):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((self.target_server_ip, self.socket_port))
        soc.send(json.dumps(message).encode("utf8")) # we must encode the string to bytes\
        soc.close()
        logging.info('Socket Closed')



class UDP_SOCKET:
    """
    UDP SOCKET with Logstsh
    """

    def __init__(self, ip, port):
        self.target_server_ip = ip
        self.socket_port = port

    def socket_logstash_handler(self, message):
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        soc.connect((self.target_server_ip, self.socket_port))
        soc.send(json.dumps(message, ensure_ascii=False).encode("utf8")) # we must encode the string to bytes\
        soc.close()
        logging.info('Socket Closed')


if __name__ == '__main__':

    '''
    python ./ELK-config/logstash/logstash-socket.py --host localhost
    '''
    parser = argparse.ArgumentParser(description="Send message to logstash server based on socket using this script")
    parser.add_argument('--host', dest='host', default="localhost", help='logstash host')
    args = parser.parse_args()
    
    if args.host:
        host = args.host

    buffer = SOCKET_JSON()    
    buffer.socket_json_push('create_date', 'SNTC2020021821575900000004')
    buffer.socket_json_push('request_server_ip', '127.0.0.1')
    print('\n', buffer.get_socket_json_pop())

    TCP_SOC = TCP_SOCKET(host, 5958)\
        .socket_logstash_handler(buffer.get_socket_json_pop())

    # message = "{'create_date' : 'SNTC2020022813562500000003', 'request_server_ip' : '172.31.245.94', 'key' : 'doc0900bf4b9ef20165', 'company_code' : '30', 'system_id' : 'law', 'login_id' : 'euiyoung.hwang', 'Sentence' : '본 계약은 포스코의 마그네슘제련공장 등 위탁설비이하 위탁설비의 운영 가동 및 유지 보전에 필요한 일상점검 정기점검 수리 등 위탁업무 전반에 대해 포스코와 수탁운영사간의 상호 역할과 책임 사고발생시 대응책임과 손해배상 생산성 향상을 위한 성과보상의 범위에 관하여 규정한다..', 'Predict' : '__label__pos', 'Percent': '1.0'}"
    # for loop in range(0, 30):
    #     message ="create_date : SNTC2020022813562500000003, request_server_ip : 172.31.245.94, key : doc0900bf4b9ef20165, company_code : 30, system_id : law, login_id : euiyoung.hwang, Sentence : 본 계약은 포스코의 마그네슘제련공장 등 위탁설비이하 위탁설비의 운영 가동 및 유지 보전에 필요한 일상점검 정기점검 수리 등 위탁업무 전반에 대해 포스코와 수탁운영사간의 상호 역할과 책임 사고발생시 대응책임과 손해배상 생산성 향상을 위한 성과보상의 범위에 관하여 규정한다.., Predict : __label__pos, Percent: 1.0"
    #     UDP_SOC = UDP_SOCKET(SOCKET_SERVER_IP, 5959)\
    #         .socket_logstash_handler(message)
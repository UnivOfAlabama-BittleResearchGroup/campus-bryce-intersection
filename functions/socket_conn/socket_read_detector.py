import socket
import csv

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

fields = ['interval_begin', 'interval_end', 'interval_id', 'interval_nVehContrib', 'interval_flow',
          'interval_occupancy', 'interval_speed', 'interval_harmonicMeanSpeed', 'interval_length',
          'interval_nVehEntered']


def run(csv_file_path):
    with open(csv_file_path, 'w+') as file:
        csv_writer = csv.writer(file, )
        csv_writer.writerow(fields)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()

            try:
                with conn:
                    print('Connected by', addr)
                    save_data = ''
                    while True:

                        data = conn.recv(1024)
                        decoded_data = data.decode("utf-8")
                        end = False
                        decoded_data = f'{save_data}{decoded_data}'

                        while not end:

                            list_data = [string.strip() for string in decoded_data.split('\n') if string]
                            save_data = []

                            for i,local_data in enumerate(list_data):

                                # check for end character
                                if '/>' in local_data[-2:]:
                                    # This is a full line
                                    if '<interval' in local_data[:9]:

                                        csv_writer.writerow([item.split(" ")[0].replace('"', '')
                                                             for i,item in enumerate(local_data[9:-2].split("=")[1:])])

                                elif (i >= len(list_data)-1) and (len(local_data) > 0):
                                    if local_data[-1] == '>':
                                        local_data = f'{local_data}\n'
                                    if (local_data[-1] == '"') and (local_data[-2] != '='):
                                        #  add a necessary space:
                                        local_data = f'{local_data} '
                                    save_data.append(local_data)

                            save_data = "".join(save_data)

                            end = True
            finally:
                conn.close()
                file.close()
                print("Detector Output Listener Connection Closed")


if __name__ == "__main__":

    run('detector_OUTPUT_.csv')

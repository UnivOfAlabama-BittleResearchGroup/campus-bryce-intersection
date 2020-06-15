import socket
import csv

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65433  # Port to listen on (non-privileged ports are > 1023)

fields = ['timestep_time',
          'vehicle_id',
          'vehicle_eclass',
          'vehicle_CO2',
          'vehicle_CO',
          'vehicle_HC',
          'vehicle_NOx',
          'vehicle_PMx',
          'vehicle_fuel',
          'vehicle_electricity',
          'vehicle_noise',
          'vehicle_route',
          'vehicle_type',
          'vehicle_waiting',
          'vehicle_lane',
          'vehicle_pos',
          'vehicle_speed',
          'vehicle_angle',
          'vehicle_x',
          'vehicle_y']


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
                    time = "0.00"
                    save_data = ''

                    while True:

                        data = conn.recv(1024)
                        decoded_data = data.decode("utf-8")
                        end = False
                        decoded_data = f'{save_data}{decoded_data}'

                        while not end:

                            list_data = [string.strip() for string in decoded_data.split('\n') if string]
                            save_data = []

                            for i, local_data in enumerate(list_data):

                                # check for time
                                if '<timestep' in local_data:
                                    time_index = decoded_data.find('<timestep', end)
                                    end_index = decoded_data.find(">", time_index + 15)
                                    time = decoded_data[time_index + 15:end_index].replace('"', '')

                                # check for end character
                                if '/>' in local_data[-2:]:
                                    # This is a full line
                                    if '<vehicle' in local_data[:8]:
                                        csv_writer.writerow([time] + [item.split(" ")[0].replace('"', '')
                                                                      for i, item in
                                                                      enumerate(local_data[8:-2].split("=")[1:])])

                                elif (i >= len(list_data) - 1) and (len(local_data) > 0):
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
                print("Emissions Output listener Connection closed")


if __name__ == '__main__':
    run('../../06_post_processing/experimental/emissions_OUTPUT_.csv')

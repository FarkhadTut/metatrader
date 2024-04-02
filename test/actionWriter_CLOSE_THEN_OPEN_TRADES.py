from datetime import datetime
import time
import os
import copy, sys
import pandas as pd
import numpy as np
import json
from .output import output

FOLDER = 'C:\\Users\\Фархад\\AppData\\Roaming\\MetaQuotes\\Tester\\36A64B8C79A6163D85E6173B54096685\\Agent-127.0.0.1-3000\\MQL5\\Files'
class actionWriter():
    def __init__(self, trading_algrithm):
        self.trading_algrithm = trading_algrithm

    def write_strategies(self, data):
        out_filename = 'action_test.txt'
        out_filename = os.path.join(FOLDER, out_filename)
        with open(out_filename, 'w') as outfile:
            json.dump(data, outfile)
        

        

    def save2csv(self,output_save, predict_result, contents, signal, prev_signal, df):
        output_save.save_csv(contents, df, signal, prev_signal, predict_result)


    
    def cleanFile(self, filename):
        del_f = open(filename, "w")
        del_f.close()
        

    def run(self):
        filename = "time_close_csv_test.csv"
        filename = os.path.join(FOLDER, filename)
        pre_Timebar = 0
        output_save = output()
        check_point = 0

        if os.path.isfile(filename) and os.stat(filename).st_size != 0:
            print("File exist and not empty")

            while True:
                if os.stat(filename).st_size != 0:
                    try:
                        with open(filename, encoding='utf-16') as f:
                            contents = f.read()
                        # you may also want to remove whitespace characters like `\n` at the end of each line
                        contents = contents.splitlines()
                        contents = [x.split('\t') for x in contents]
                        for i in range(len(contents)):
                            contents[i][0] = datetime.strptime(contents[i][0], '%Y.%m.%d %H:%M:%S')
                            contents[i][1] = float(contents[i][1]) #open
                            contents[i][2] = float(contents[i][2]) #high
                            contents[i][3] = float(contents[i][3]) #low
                            contents[i][4] = float(contents[i][4]) #close
                            contents[i][5] = int(contents[i][5]) #tick value

                        newTimebar = contents[-1][0]
                        curr_position = contents[-1][-1]
                        curr_close_price = contents[-1][4]
                        if curr_position == "Ending":
                            
                            print(">>>------------------------<<<")
                            output_save.output_csv()
                            print(">>> Server Stop <<<")
                            break
                            

                        else:
                            if pre_Timebar != newTimebar:
                                pre_Timebar = copy.deepcopy(newTimebar)
                                
                                # print("Timebar: ",pre_Timebar)
                                # print("curr_close_price: ",curr_close_price)
                                # print("curr_position", curr_position)

                                # code from example2.py, send the data to the main_DecisionMaker.py
                                predict_result  = self.trading_algrithm.predict(contents)
                                if type(predict_result) is not dict:
                                    raise ValueError("Value must return a dictionary type")
                                print("predict_result","\t",predict_result)
                                
                                # write the result to txt or csv 
                                if 'close_action' in predict_result.keys():
                                    self.write_strategies({'action': predict_result['close_action']})
                                    time.sleep(0.1)
                                    del predict_result['close_action']

                                self.write_strategies(predict_result)
                                # self.cleanFile(filename)
                                
                                # self.save2csv(output_save, predict_result, contents, signal, prev_signal, df)

                                check_point += 1

                                if check_point % 50 == 0:
                                    output_save.output_csv()

                            else:
                                time.sleep(0.003)

                    except Exception as e:
                        # raise e
                        pass
                        
                else:
                    # print("File is empty")
                    time.sleep(0.001)          
        else:
            print(f"File not exist ({filename})")
# Answer grading tool


from python_files.classes import *
from python_files.import_export_functions import *

# (1) import raw data--------------------------------------------------------

#question_1 = import_mohler_txt(question_id="Q1", import_file="Mohler_Q1.txt")
question_list = import_mohler_txt(question_id="Q")
question = question_list[0]
original_file_name = question_list[1]


# (3) Generate an Event-log from data----------------------------------------

question.pre_process_question()
question.generate_event_log()
question.event_log.export_event_log_xes(original_file_name=original_file_name)


#(4) Import constraints from mining-output-----------------------------------

question.event_log.import_mined_declare(original_file_name=original_file_name)


# (5) Check which constraints are in which answers---------------------------

question.check_constraints()

#-------Export grades + number of co-existence-----------------

export_data_as_csv(question=question,original_file_name=original_file_name)






#

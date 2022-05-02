# Answer grading functions
from python_files.classes import *
import csv

original_file_name = ""
#----------------Mohler2009 import from txt file--------------------------------
def import_mohler_txt(question_id = "Q", import_file=None):
    if import_file is None:
        import_file = askopenfilename(title="Import Mohler2009 question")
        original_file_name = str(import_file)
    with open(import_file, encoding="utf-8") as raw_dataset_file:
        raw_dataset_txt = raw_dataset_file.read()
    dataset_list = raw_dataset_txt.split("\n") # Split raw dataset into a list
    for i in range(len(dataset_list)):
        cleared_line = (dataset_list[i].replace("\t","").
                            replace("<br>","").
                            replace("-", "")
                        )
        dataset_list[i] = cleared_line
    question = ""
    for line in dataset_list:
        if "Question:" in line:
            question = line
            dataset_list.remove(line)
            question = question.replace("Question:", "")
    teacher_answers = []
    for line in dataset_list:
        if "Answer:" in line:
            teacher_answer = line.replace("Answer:", "")
            teacher_answers.append(teacher_answer)
            dataset_list.remove(line)
    answer_list = []
    for line in dataset_list:
        if "[" in line or "]" in line:
            answer_list.append(line)

    new_question = Question(q_id = question_id, q_text=question)
    for i in teacher_answers:
        teacher_answer = Teacher_answer(question=new_question,answer_text=i)
    for i in answer_list:
        first_marker = i.find("[")
        second_marker = i.find("]")
        student_answer = Student_answer(question = new_question,
                                        answer_text = i[second_marker+1:],
                                        student_id = i[first_marker+1:second_marker],
                                        grade = i[:first_marker])

    return [new_question, original_file_name]


def export_data_as_csv(question=None, export_file=None, original_file_name=""):
    if question is None or type(question) is not Question:
        print("Please enter a question-object")
        return False
    if export_file is None:
        export_file = asksaveasfilename(
                        title="Export Analysis Data for: " + original_file_name,
                        filetypes=[('CSV','*.csv')],
                        defaultextension="csv",
                        initialfile=question.q_id + "_analysis")
    if export_file != "":
        header = ["Student_id","grade","number_of_constraints"]
        with open(export_file,"w",newline="") as file:
            writer=csv.writer(file)
            writer.writerow(header)
            for answ in question.student_answers:
                writer.writerow([answ.student_id,
                                answ.grade,
                                len(answ.fulfilled_constraints)])
    return export_file

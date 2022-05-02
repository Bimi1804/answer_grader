# declarative answer grader: class definitions

#----------IMPORTS-----------------------------------------------------
# import structure for .xes event-logs files:
from python_files.xes_structure import *

# import nltk-package for NLP pre-processing:
import nltk # nltk package: https://www.nltk.org/data.html
from nltk.stem import WordNetLemmatizer # for lemmatization
from nltk.corpus import stopwords # for stopword removal
from nltk.tokenize import word_tokenize # for stopword removal
# set variables for NLP pre-processing:
lemmatizer = WordNetLemmatizer() # lemmatization function
stop_words = set(stopwords.words('english')) # english stop-words
removable_items = [".", ","] # additional strings that should be removed

# import tkinter for dialog-windows:
import tkinter as tk
from tkinter.filedialog import askopenfilename # dialog for opening a file
from tkinter.filedialog import asksaveasfilename # dialog for saving a file
root = tk.Tk()
root.withdraw()

# import abstract base class (abc):
from abc import (ABC,abstractmethod) # for abstract class and abstract method



#------Global Functions----------------------------------------------------
class Tools:
    """"
    Class for all global functions

    Methods
    --------
    pre_process(original_text) : str[0..*]
        Pre-processes a string into a list of words.
    """
    def __init__(self):
        pass
    def pre_process(self,original_text):
        """
        Pre-processes an original_text as string into processed_text as a list.

        Parameters
        ----------
        original_text : str
            The original_text as a string

        Returns
        -------
        processed_text : str[0..*]
            A list with indidivual words
         """

        # transform words into only lowercase and tokenize them:
        word_tokens = word_tokenize(original_text.lower())
        words_without_stop = [] # store non-stop-words
        for w in word_tokens:
            # append non-stop-words to words_without_stop:
            if w not in stop_words:
                words_without_stop.append(w)

        # lemmatization of words_without_stop:
        processed_text = [] # store lemmatized words
        for word in words_without_stop:
            lemma_word = lemmatizer.lemmatize(word)
            processed_text.append(lemma_word)

        # remove additional words or symbols:
        final_processed_text = [] # final processed words
        for word in processed_text:
            if word not in removable_items:
                final_processed_text.append(word)
        return final_processed_text
tools = Tools() # instantiation of the Tools class

#---------------------------Answer-grading Classes------------------------------

class Question:
    """
    The Question of an Exam

    Parameters
    ----------
    q_id : str
        To directly store the question ID
    q_text : str
        To directly store the question text

    Attributes
    ----------
    q_id : str
        Store the question ID
    q_text : str
        Store the question text
    pre_processed_question_text : str[0..*]
        The question text after NLP pre-processing
    student_answers : Student_answer[0..*]
        Holds the student answers
    teacher_answers : Teacher_answer[0..*]
        Holds the teacher answers
    event_log : Event_log
        Holds the Event_log

    Methods
    ---------
    pre_process_question(): Question
        Pre-processing the original question,student- and teacher-answer texts
    generate_event_log(): Event_log
        Generate an Event_log object
    check_constraints(): Question
        Check which mined constraints are fulfilled by the answers
    calculate_rightness():
        Calculate the "rightness" of answers
    """
    def __init__(self,q_id,q_text):
        self.q_id = q_id
        self.q_text = q_text
        self.pre_processed_question_text = []
        self.student_answers = []
        self.teacher_answers = []
        self.event_log = ""

    def pre_process_question(self):
        """
        NLP pre-processing of the question text and the student- and teacher-
        answers

        Stores the processed text in the objects (Question, Student_answer,
                                                  Teacher_answer)

        Parameters
        ----------
        None

        Returns
        -------
        self
            Returns the Question object
        """
        # Use the pre-process method from the Tools class:
        self.pre_processed_question_text = tools.pre_process(self.q_text)
        for i in self.student_answers:
            i.pre_processed_answer_text = tools.pre_process(i.answer_text)
        for i in self.teacher_answers:
            i.pre_processed_answer_text = tools.pre_process(i.answer_text)
        return self

    def generate_event_log(self):
        """
        Generates an event-log from all student answers in a .xes format

        Parameters
        ----------
        None

        Returns
        -------
        self.event_log
            The created Event_log object
        """
        log_traces = "" # store traces(answers) of the log
        for answ in self.student_answers:
            trace_events = "" # store events(words) of a trace
            order = 1 # the order of the events(words)
            for word in answ.pre_processed_answer_text:
                # use xes-template for events and fill {word} and {order}:
                trace_events += xes_template.xes_event.format(word=word,
                                                                order=order)
                order += 1 # increment order
            # use xes-template for traces and fill with {student_id} and
            # {trace_events}:
            log_traces += xes_template.xes_trace.format(trace_id=answ.student_id,
                                                        events=trace_events)
        # use xes-template for log-head and fill with {log_traces}:
        xes_log = xes_template.xes_head.format(traces=log_traces)
        # Create a new Event_log object with xes_log as log-string:
        self.event_log = Event_log(question=self, event_log_string=xes_log)
        return self.event_log

    def check_constraints(self):
        """
        Check which constraints are fulfilled by the student_answers

        The fulfilled constraints of each answer are stored in the
        Student_answer object
        """
        # loop over all discovered constraints:
        for const in self.event_log.mined_constraints:
            # loop over the student answers:
            for answ in self.student_answers:
                # check if the answer fulfills the constraint:
                if const.constraint_type.conformance_check(const,answ) is True:
                    # Append constraint to the answer's fulfilled constraints
                    answ.fulfilled_constraints.append(const)
        return self

    def calculate_rightness():
        # calculate the "rightness of answers"
        # This function will create an event-log an declaratively mine for
        # constraints...
        pass

class Answer(ABC):
    """
    The abstract Answer class

    Parameters
    ----------
    question : Question
        The Question object to which the answer belongs
    answer_text : str
        The answer text as a string

    Attributes
    ----------
    question : Question
        To store the Question object
    answer_text : str
        To store the answer text
    pre_processed_answer_text : str[0..*]
        A list of words that were processed from answer_text
    fulfilled_constraints : Constraint[0..*]
        A list with all fulfilled Constraint objects
    """
    def __init__(self,question,answer_text):
        if type(question) is not Question:
            return False
        self.question = question
        self.answer_text = answer_text
        self.pre_processed_answer_text = []
        self.fulfilled_constraints = []

class Teacher_answer(Answer):
    """
    Sub-class of Answer

    A teacher answer of a question

    Adds itself to the list of teacher answers of the question when created

    Additional Parameters
    --------------------
    None
    """
    def __init__(self,question,answer_text):
        super().__init__(question,answer_text)
        question.teacher_answers.append(self) # Adds the object to the
                                              # teacher_answers list of the
                                              # Question object that is stored
                                              # in self.question

class Student_answer(Answer):
    """
    Sub-class of Answer

    A student answer of a question

    Adds itself to the list of student answers of the question when created

    Additional Parameters
    ---------------------
    student_id : str
        The student-ID of a student, so answers can be assigned to the right
        student
    grade = None : str
        The grade or points that were given to the student answer

    Additional Attributes
    --------------------
    student_id : str
        To store student_id
    calculated_rightness : int
        To store the calculated rightness of a student answer
    grade : str
        To store grade
    """
    def __init__(self,question,answer_text,student_id,grade=None):
        super().__init__(question,answer_text)
        self.student_id = student_id
        self.calculated_rightness = None
        self.grade = grade
        question.student_answers.append(self) # Adds the object to the
                                              # student_answers list of the
                                              # Question object that is stored
                                              # in self.question

class Event_log:
    """
    The event-log that is generated for a question

    Parameters
    ----------
    question : Question
        The Question object which the Event_log belongs to
    event_log_string : str
        The actual event-log in a .xes structure as a string

    Attributes
    ----------
    question : Question
        To store question
    event_log_xes : str
        To store event_log_string
    mined_activities : Activity[0..*]
        To store the mined activities of the event-log
    mined_constraints : Constraint[0..*]
        To store the mined constraints of the event-log

    Methods
    -------
    export_event_log_xes(output_file=None,original_file_name=""): str
        Exports the event-log in a .xes file
    import_mined_declare(import_file=None,original_file_name=""): Event_log
        Imports a .decl file to store the discovered activities and constraints
    mining()
        This would be the included miner
    """
    def __init__(self, question, event_log_string):
        self.question = question
        self.event_log_xes = event_log_string
        self.mined_activities = []
        self.mined_constraints = []

    def export_event_log_xes(self,output_file=None,original_file_name=""):
        """
        Exports the event-log as a .xes file

        Parameters
        ----------
        output_file = None : str
            The file path to the file where the event-log should be stored.
            If this is None, then a dialog window will open to save the file.
        original_file_name : str
            The file name of the raw input file for the question. This is
            displayed in the file-saving-window.

        Returns
        -------
        output_file : str
            Returns the path to the output_file
        """
        if output_file is None:
            # Open file dialog to type in file-name (only .xes):
                # Default file-name is question-ID + "_log"
            output_file = asksaveasfilename(
                                title="Export event-log for: " +
                                                original_file_name,
                                filetypes=[('Event-Log', '*.xes')],
                                defaultextension="xes",
                                initialfile=self.question.q_id + "_log")
        if output_file != "": # Only write to the file if it exists/has a name
            with open(output_file, "w") as file_xes:
                file_xes.write(self.event_log_xes)
        return output_file

    def import_mined_declare(self,import_file=None,original_file_name=""):
        """
        Import a .decl file and create Activity and Constraint objects based on
        the content of the .decl file.

        Activity and Constraint objects will be created.

        Parameters
        ----------
        import_file=None : str
            The file path to the file that should be imported.
            If this is None, then a dialog window will open to choose the file.
        original_file_name : str
            The file name of the raw input file for the question. This is
            displayed in the file-opening-window.

        Returns
        -------
        self
        """
        if import_file is None:
            # open file-dialog to choose the .decl import-file:
            import_file = askopenfilename(title="Import DECLARE file for:" +
                                                        original_file_name,
                                            filetypes=[('DECLARE', '*.decl')])
        with open(import_file, "r") as raw_decl:
            raw_decl_file = raw_decl.read()
        decl_file = raw_decl_file.split("\n") # split at each new line
        decl_file.remove("") # remove any empty lines

        constraints = [] # store the lines that define constraints
        for line in decl_file:
            # if the line defines an activity, then create and store a new
            # Activity object:
            if "activity" in line:
                new_activity = Activity(self, line[len("activity")+1:])
            else:
                # if not, then append the line to the constraints list:
                constraints.append(line)

        for line in constraints:
            # Structure of .decl files: <constraint>[<activity_a>, <activity_b>]
            first_marker = line.find("[") # Find the index of  [
            second_marker = line.find("]") # Find the index of ]
            constraint = line[:first_marker] # This is the <constraint>
            activities = line[first_marker+1:second_marker] # Both activities
            mid_marker = activities.find(",") # The marker between the
                                              # activities
            activity_a_word = activities[:mid_marker] # Activity A
            activity_b_word = activities[mid_marker+2:] # Activity B
            for act in self.mined_activities:
                # Get the Activity objects for the activities A and B of the
                # constraint
                if act.activity_text == activity_a_word:
                    activity_a = act
                if act.activity_text == activity_b_word:
                    activity_b = act
            for c_t in constraint_types:
                # Get the constraint type of the constraint
                if c_t.constraint_type_name == constraint:
                    constraint_type = c_t
            # Create a new constraint object
            new_constraint = Constraint(activity_a, activity_b, constraint_type)
        return self

    def mining():
        #This would be the declarative process Miner
        pass

class Activity:
    """
    An Activity that was discovered from an event-log

    Appends itself to the mined_activities-list of the Event_log object that
    created it.

    Parameters
    ----------
    event_log : Event_log
        The Event_log objects to which the Activity belongs
    activity_text : str
        The actual text (word) of the activity
    activity_support=100 : int
        The support of the activity that was discovered by the miner

    Attributes
    ----------
    event_log : Event_log
        Store event_log
    activity_text : str
        Store activity_text
    activity_support : int
        Store activity_support
    """
    def __init__(self,event_log,activity_text,activity_support=100):
        self.event_log = event_log
        self.activity_text = activity_text
        self.activity_support = activity_support
        self.event_log.mined_activities.append(self)

class Constraint:
    """
    A constraint that was discovered from an event-log

    Appends itself to the mined_constraints-list of the Event_log object that
    created it.

    Parameters
    ---------
    activity_a : Activity
        The activity A of the constraint
    activity_b : Activity
        The activity B of the constraint
    constraint_type : Constraint_type
        The constraint-type (constraint-template) of the constraint
    constraint_support=100 : int
        The support of the constraint that was discovered by the miner

    Attributes
    ----------
    activity_a : Activity
        To store activity A
    activity_b : Activity
        To store activity B
    constraint_type : Constraint_type
        To store the constraint type
    constraint_support : int
        To store the constraint support
    correctness : str
        The "correctness" of a constraint ("right", "wrong", "neutral")
    """

    def __init__(self,activity_a, activity_b,
                constraint_type, constraint_support=100):
        # Type-checking of inputs:
        if type(constraint_type) is not Constraint_type:
            print("Constraint-type is not a Constraint_type-object")
            return False
        if type(activity_a) is not Activity:
            print("Activity-A is not an Activity-object")
            return False
        if type(activity_b) is not Activity:
            print("Activity-B is not an Activity-object")
            return False
        self.activity_a = activity_a
        self.activity_b = activity_b
        self.constraint_type = constraint_type
        self.constraint_support = constraint_support
        self.correctness = ""
        self.activity_a.event_log.mined_constraints.append(self)

class Constraint_type:
    """
    A Constraint-type (constraint-template)

    Parameters
    ----------
    constraint_type_name : str
        The name of the constraint-type

    Attributes
    ----------
    constraint_type_name : str
        To store the constraint_type_name

    Methods
    -------
    conformance_check(constraint,answer) : bool
        Checks if the given answer fulfills the given constraint
    __co_existence_check(act_a,act_b,processed_answer): bool
        Checks if Co-Existence[A,B] is fulfilled by an answer
    __precedence_check(act_a,act_b,processed_answer): bool
        Checks if Precedence[A,B] is fulfilled by an answer
    """
    def __init__(self,constraint_type_name):
        self.constraint_type_name = constraint_type_name

    def conformance_check(self,constraint,answer):
        """
        Checks if the given answer fulfills the given constraint

        Parameters
        ----------
        constraint : Constraint
            The constraint that the answer will be checked for
        answer : Answer
            The answer that will be checked (a subclass of Answer)

        Returns
        -------
        return_value : bool
            True - the answer fulfills the constraint
            False - the answer does not fulfill the constraint
        """
        # Type-checking of inputs:
        if type(constraint) is not Constraint:
            print("Constraint given is not a Constraint-Object")
            return False
        if not issubclass(type(answer),Answer):
            print("Answer given is not an Answer-Object")
            return False

        act_a = constraint.activity_a.activity_text # the text-string of act. A
        act_b = constraint.activity_b.activity_text # the text-string of act. B
        processed_answer = answer.pre_processed_answer_text # pre-processed text
                                                            # of the answer
        return_value = False
        # Use the conformance check that belongs to the constraint-type
        if self.constraint_type_name == "Co-Existence":
            return_value = self.__co_existence_check(act_a,act_b,
                                                        processed_answer)
        if self.constraint_type_name == "Precedence":
            return_value = self.__precedence_check(act_a,act_b,
                                                        processed_answer)
        return return_value

    # Unary Constraints:
    def __absence_1_check():
        pass

    def __absence_2_check():
        pass

    def __absence_3_check():
        pass

    def __exactly_1_check():
        pass

    def __exactly_2_check():
        pass

    def __existence_1_check():
        pass

    def __existence_2_check():
        pass

    def __existence_3_check():
        pass

    def __init_check():
        pass


    #Binary Positive Constraints:
    def __alternate_precedence_check():
        pass

    def __alternate_response_check():
        pass

    def __alternate_succession_check():
        pass

    def __chain_precedence_check():
        pass

    def __chain_response_check():
        pass

    def __chain_succession_check():
        pass

    def __co_existence_check(self,act_a,act_b,processed_answer):
        """
        Checks if the answer fulfills Co-Existence[A,B]

        Parameters
        ----------
        act_a : str
            The actual text (word) of activity A
        act_b : str
            The actual text (word) of activity B
        processed_answer : str[0..*]
            the list of processed words of the answer

        Returns
        -------
        True -> If the answer fulfills the constraint
        False -> If the answer does not fulfill the constraint
        """
        # Check if A and B are both NOT in the answer:
        if act_a not in processed_answer and act_b not in processed_answer:
            return True
        # Check if A and B are both in the answer:
        if act_a in processed_answer and act_b in processed_answer:
            return True
        else:
            # If only A or only B is in the answer:
            return False

    def __precedence_check(self,act_a,act_b,processed_answer):
        """
        Checks if the answer fulfills Precedence[A,B]

        Parameters
        ----------
        act_a : str
            The actual text (word) of activity A
        act_b : str
            The actual text (word) of activity B
        processed_answer : str[0..*]
            the list of processed words of the answer

        Returns
        -------
        True -> If the answer fulfills the constraint
        False -> If the answer does not fulfill the constraint
        """
        checking = processed_answer # store the answer
        if act_b not in checking:
            # if B not in the answer:
            return True
        while act_b in checking:
            # as long as B is in the answer:
            act_b_index = checking.index(act_b) # find index of B
            if act_a not in checking[:act_b_index]:
                # If A is not before B:
                return False
            # Continue with the part of the answer after the first B
            checking = checking[act_b_index+1:]
        # If the answer does not violate the constraint:
        return True

    def __responded_existence_check():
        pass

    def __response_check():
        pass

    def __succession_check():
        pass

    # Binary Negative Constraints:
    def __not_chain_succession_check():
        pass

    def __not_co_existence_check():
        pass

    def __not_succession_check():
        pass




constraint_types = [] # A list with all implemented constraint-types
coexistence = Constraint_type("Co-Existence") # instantiation of "Co-Existence"
constraint_types.append(coexistence)

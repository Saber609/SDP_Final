from abc import ABC, abstractmethod
from typing import List

class QuestionFactory(ABC):
    @abstractmethod
    def create_question(self, text: str) -> 'Question':
        pass

class ResultObserver(ABC):
    @abstractmethod
    def update(self, result: int):
        pass

class Question(ABC):
    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def get_answer(self) -> str:
        pass

    @abstractmethod
    def check_answer(self, user_answer: str) -> bool:
        pass

class QuestionDecorator(Question):
    def __init__(self, question: 'Question'):
        self._question = question

    @abstractmethod
    def get_text(self) -> str:
        pass

class QuizSingleton:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(QuizSingleton, cls).__new__(cls)
            cls._instance.quizzes = []
        return cls._instance

class AnswerAdapter(ABC):
    @abstractmethod
    def get_user_input(self) -> str:
        pass

class ScoringStrategy(ABC):
    @abstractmethod
    def calculate_score(self, user_answers: List[str], correct_answers: List[str]) -> int:
        pass

class PercentageScoringStrategy(ScoringStrategy):
    def calculate_score(self, user_answers: List[str], correct_answers: List[str]) -> int:
        correct_count = sum(1 for user, correct in zip(user_answers, correct_answers) if user == correct)
        total_questions = len(correct_answers)
        return int((correct_count / total_questions) * 100)

class MultipleChoiceQuestion(Question):
    def __init__(self, text, choices, correct_answer):
        self.text = text
        self.choices = choices
        self.correct_answer = correct_answer

    def get_text(self) -> str:
        return self.text

    def get_answer(self) -> str:
        return self.correct_answer

    def check_answer(self, user_answer: str) -> bool:
        return user_answer == self.correct_answer

class TrueFalseQuestion(Question):
    def __init__(self, text, correct_answer):
        self.text = text
        self.correct_answer = correct_answer

    def get_text(self) -> str:
        return self.text

    def get_answer(self) -> str:
        return self.correct_answer

    def check_answer(self, user_answer: str) -> bool:
        return user_answer == self.correct_answer

class StandardQuestionFactory(QuestionFactory):
    def create_question(self, question_type: str, text: str, *args, **kwargs) -> Question:
        if question_type == 'MultipleChoice':
            return self.create_multiple_choice_question(text, *args, **kwargs)
        elif question_type == 'TrueFalse':
            return self.create_true_false_question(text, *args, **kwargs)
        else:
            raise ValueError("Invalid question type.")

    def create_multiple_choice_question(self, text: str, choices: List[str],
                                        correct_answer: str) -> MultipleChoiceQuestion:
        return MultipleChoiceQuestion(text, choices, correct_answer)

    def create_true_false_question(self, text: str, correct_answer: str) -> TrueFalseQuestion:
        return TrueFalseQuestion(text, correct_answer)

class ConsoleResultObserver(ResultObserver):
    def update(self, result: int):
        print(f"\nQuiz completed. Your score: {result}%\n")

class ConsoleAnswerAdapter(AnswerAdapter):
    def get_user_input(self) -> str:
        return input("Your answer: ")

class ConsoleInterface:
    def __init__(self, answer_adapter: AnswerAdapter, scoring_strategy: ScoringStrategy):
        self.quiz_questions = []
        self.result_observer = ConsoleResultObserver()
        self.answer_adapter = answer_adapter
        self.scoring_strategy = scoring_strategy

    def create_quiz(self):
        print("\nCreating a new quiz...")

        question_factory = StandardQuestionFactory()

        while True:
            print("\n1. Add Multiple Choice Question")
            print("2. Add True/False Question")
            print("3. Finish creating quiz")
            choice = input("Select an option (1-3): ")

            if choice == '1':
                question_text = input("Enter the multiple-choice question text: ")
                choices = input("Enter the choices for the question (comma-separated): ").split(',')
                correct_answer = input("Enter the correct answer (one of the choices): ")
                question = question_factory.create_question('MultipleChoice', question_text, choices, correct_answer)
                self.quiz_questions.append(question)
            elif choice == '2':
                question_text = input("Enter the True/False question text: ")
                correct_answer = input("Enter the correct answer (True or False): ")
                question = question_factory.create_question('TrueFalse', question_text, correct_answer)
                self.quiz_questions.append(question)
            elif choice == '3':
                print("Quiz creation completed.")
                break
            else:
                print("Invalid choice. Please try again.")

    def take_quiz(self):
        if not self.quiz_questions:
            print("No quiz available. Please create a quiz first.")
            return

        print("\nTaking the quiz...")
        user_answers = []

        for question in self.quiz_questions:
            print(f"\nQuestion: {question.get_text()}")

            if isinstance(question, MultipleChoiceQuestion):
                print("Choices: " + ", ".join(question.choices))
            user_answer = self.answer_adapter.get_user_input()  # Use the adapter here

            user_answers.append(user_answer)

        score = self.calculate_score(user_answers, self.quiz_questions)
        self.result_observer.update(score)

    def calculate_score(self, user_answers, questions):
        correct_answers = [question.get_answer() for question in questions]
        return self.scoring_strategy.calculate_score(user_answers, correct_answers)

    def start(self):
        print("Welcome to the Quiz/Survey Console App!")
        while True:
            print("\n1. Create Quiz")
            print("2. Take Quiz")
            print("3. Exit")
            choice = input("Select an option (1-3): ")

            if choice == '1':
                self.create_quiz()
            elif choice == '2':
                self.take_quiz()
            elif choice == '3':
                print("Exiting the application. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    answer_adapter = ConsoleAnswerAdapter()
    scoring_strategy = PercentageScoringStrategy()
    console_interface = ConsoleInterface(answer_adapter, scoring_strategy)
    console_interface.start()
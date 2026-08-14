import json # package
from pathlib import Path # pathlib package & Path class or sub package


class Quiz:
    """퀴즈 한 문제를 담당하는 클래스"""

    def __init__(self, question, choices, answer): # Quiz class에서 가장 먼저 실행 / question, choices, answer 데이터
        self.question = question # question 데이터를 self.question에 할당
        self.choices = choices
        self.answer = answer

        # 잘못된 퀴즈가 만들어지는 것을 방지한다.
        if not self.question: # self.question이 비어있을 경우 실행
            raise ValueError("문제는 비어 있을 수 없습니다.")

        if len(self.choices) != 4: # self.choices 개수가 4와 같지 않을때 실행
            raise ValueError("선택지는 반드시 4개여야 합니다.")

        if not 1 <= self.answer <= 4: # self.answer가 1이상 4이하가 아닐 경우 실행
            raise ValueError("정답은 1~4 사이의 숫자여야 합니다.")

    def display(self, number):
        """문제와 선택지를 가독성있게 출력한다."""

        print("-" * 40)
        print(f"[문제 {number}]") 
        print(self.question)
        print()

        for index, choice in enumerate(self.choices, start=1): # enumerate 자료형 타입을 사용하여 인덱싱
            print(f"{index}. {choice}") # index 1부터 시작

    def is_correct(self, user_answer): 
        """사용자의 답이 실제 정답과 같은지 확인한다."""

        return self.answer == user_answer # 사용자 입력값 user_answer와 self.answer 값이 같으면 반환

    def to_dict(self):
        """Quiz 객체를 JSON에 저장 가능한 dict로 바꾼다."""

        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        } 


class QuizGame:
    """게임 전체를 관리하는 클래스"""

    def __init__(self):
        
        self.state_file = Path(__file__).resolve().parent / "state.json" # state.json 파일의 경로 찾기

        self.quizzes = [] # 퀴즈 목록을 저장할 리스트

        self.best_score = 0 # 최고 점수 저장
        self.best_correct = 0 # 최고 기록에서 맞힌 문제 수
        self.best_total = 0 # 최고 기록 당시 전체 문제 수

        self.load_state() # state.json 파일을 읽어 이전 데이터를 불러온다. 저장된 파일이 있으면 그 기록을 덮어쓴다.

    def create_default_quizzes(self):
        """파일이 없거나 손상됐을 때 사용할 기본 퀴즈""" # state.json 파일이 없거나 손상됐을 때 기본으로 사용할 퀴즈 생성

        return [
            Quiz(
                "다음 중 커피가 들어간 음료가 아닌것은?",
                ["아메리카노", "레몬에이드", "카페라떼", "카페모카"],
                2,
            ),
            Quiz(
                "스무디 종류가 아닌것은?",
                ["블루베리스무디", "딸기라떼", "딸기요거트스무디", "코코넛커피스무디"],
                2,
            ),
            Quiz(
                "디저트의 종류가 아닌것은?",
                ["아이폰 17", "소금빵", "초코쿠키", "레몬마카롱"],
                1,
            ),
            Quiz(
                "아이스티에 샷을 추가한 음료의 줄임말은?",
                ["뜨아", "아아", "아샷추", "딸라"],
                3,
            ),
            Quiz(
                "시나몬 가루가 올려진 커피 이름은?",
                ["초코라떼", "키위주스", "카푸치노", "카라멜 마끼아또"],
                3,
            ),
        ]

    def reset_to_default(self):
        """퀴즈와 점수를 기본 상태로 초기화한다."""

        self.quizzes = self.create_default_quizzes() # 기본 퀴즈를 self.quizzes에 할당

        self.best_score = 0
        self.best_correct = 0
        self.best_total = 0

    def load_state(self):
        """state.json에서 데이터를 불러온다."""

        try: # 예외처리
            with open(self.state_file, "r", encoding="utf-8") as file: # state.json을 읽어 file 변수에 할당
                data = json.load(file) # load() : json 형태 파일을 파이썬 문법에 맞게 바꾸는 함수 >> data 변수에 할당

            if not isinstance(data, dict): # state.json != dict형 > false, data 변수의 type은 dict
                raise ValueError("저장 데이터 형식이 잘못되었습니다.")

            quiz_data_list = data.get("quizzes") # data 형태 : dict, dict class에서의 get 메서드 사용하여 quizzes라는 key의 value값을 quiz_data_list에 할당

            if not isinstance(quiz_data_list, list): # quiz_data_list != list형 >> false
                raise ValueError("퀴즈 데이터가 목록이 아닙니다.")

            loaded_quizzes = []

            for quiz_data in quiz_data_list:
                if not isinstance(quiz_data, dict): # quiz_data != dict형 >> false
                    raise ValueError("퀴즈 데이터 형식이 잘못되었습니다.")

                quiz = Quiz( # 딕셔너리 하나하나 quiz 객체 생성
                    question=quiz_data["question"], # 다음 중 커피가 들어간 음료가 아닌것은?
                    choices=quiz_data["choices"], # 아메리카노...
                    answer=quiz_data["answer"], # 2
                )
                loaded_quizzes.append(quiz)

            best_score = data.get("best_score", 0) # best_score가 key값이 없을 경우 기본값 0, 반대로 key값이 존재할 경우 value값을 best_score에 할당
            best_correct = data.get("best_correct", 0)
            best_total = data.get("best_total", 0)

            score_values = ( # 데이터가 함부로 바뀌면 안될때 튜플사용, immutable
                best_score,
                best_correct,
                best_total,
            )

            if not all(isinstance(value, int) for value in score_values): # score_value를 value에 하나씩 넣고, 형태가 int인지 확인. 맞으면 True 반환, 모두 True면 True, 하나라도 False면 False
                raise ValueError("점수 데이터는 정수여야 합니다.")

            if not 0 <= best_score <= 100: # 최고 점수가 0 이상 100 이하가 아닌 경우
                raise ValueError("최고 점수가 올바르지 않습니다.")

            if best_correct < 0: # 최고 기록에서 맞힌 문제 수가 0 미만인 경우
                raise ValueError("정답 개수가 올바르지 않습니다.")

            if best_total < 0: # 최고 기록 당시 전체 문제 수가 0 미만인 경우
                raise ValueError("문제 개수가 올바르지 않습니다.")

            if best_correct > best_total: # 최고 기록에서 맞힌 문제 수 > 최고 기록 당시 전체 문제 수
                raise ValueError("점수 상세 정보가 올바르지 않습니다.")

            self.quizzes = loaded_quizzes
            self.best_score = best_score
            self.best_correct = best_correct
            self.best_total = best_total

            print(
                f"📂 저장된 데이터를 불러왔습니다. "
                f"(퀴즈 {len(self.quizzes)}개, "
                f"최고 점수 {self.best_score}점)"
            )

        except FileNotFoundError:
            print("📂 저장 파일이 없어 기본 퀴즈를 사용합니다.")

            self.reset_to_default()
            self.save_state()

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
            KeyError,
            TypeError,
            ValueError,
            OSError,
        ):
            print("⚠️ 저장 파일을 읽을 수 없어 기본 데이터로 복구합니다.")

            self.reset_to_default()
            self.save_state()

    def save_state(self):
        """현재 데이터를 state.json에 저장한다."""

        data = {
            "quizzes": [
                quiz.to_dict()
                for quiz in self.quizzes
            ],
            "best_score": self.best_score,
            "best_correct": self.best_correct,
            "best_total": self.best_total,
        }

        try:
            with open(self.state_file, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

            return True

        except OSError:
            print("⚠️ 데이터를 파일에 저장하지 못했습니다.")
            return False

    def get_integer(self, prompt, minimum, maximum):
        """범위 안의 숫자를 입력할 때까지 반복한다."""

        while True:
            raw_value = input(prompt).strip()

            if raw_value == "":
                print("⚠️ 아무것도 입력하지 않았습니다.")
                continue

            try:
                value = int(raw_value)

            except ValueError:
                print("⚠️ 숫자를 입력해 주세요.")
                continue

            if value < minimum or value > maximum:
                print(
                    f"⚠️ {minimum}~{maximum} 사이의 "
                    f"숫자를 입력해 주세요."
                )
                continue

            return value

    def get_text(self, prompt):
        """빈 글자가 아닌 값을 입력할 때까지 반복한다."""

        while True:
            value = input(prompt).strip()

            if value == "":
                print("⚠️ 아무것도 입력하지 않았습니다.")
                continue

            return value

    def show_menu(self):
        """메인 메뉴를 출력한다."""

        print()
        print("=" * 40)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("=" * 40)

    def play_quiz(self):
        """저장된 퀴즈를 출제하고 점수를 계산한다."""

        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다.")
            return

        correct_count = 0
        total_count = len(self.quizzes)

        print()
        print(f"📝 퀴즈를 시작합니다! (총 {total_count}문제)")

        for number, quiz in enumerate(self.quizzes, start=1):
            print()

            quiz.display(number)

            user_answer = self.get_integer(
                "정답 입력: ",
                1,
                4,
            )

            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!")
                correct_count += 1

            else:
                correct_text = quiz.choices[quiz.answer - 1]

                print(
                    f"❌ 오답입니다. 정답은 "
                    f"{quiz.answer}번 "
                    f"({correct_text})입니다."
                )

        score = round(correct_count / total_count * 100)

        print()
        print("=" * 40)
        print(
            f"🏆 결과: {total_count}문제 중 "
            f"{correct_count}문제 정답! "
            f"({score}점)"
        )

        # 아직 플레이한 적이 없거나 최고 점수를 넘은 경우
        if self.best_total == 0 or score > self.best_score:
            self.best_score = score
            self.best_correct = correct_count
            self.best_total = total_count

            print("🎉 새로운 최고 점수입니다!")

        print("=" * 40)

        self.save_state()

    def add_quiz(self):
        """사용자에게 입력받아 새로운 퀴즈를 추가한다."""

        print()
        print("📌 새로운 퀴즈를 추가합니다.")

        question = self.get_text("문제를 입력하세요: ")

        choices = []

        for number in range(1, 5):
            choice = self.get_text(f"선택지 {number}: ")
            choices.append(choice)

        answer = self.get_integer(
            "정답 번호 (1-4): ",
            1,
            4,
        )

        new_quiz = Quiz(
            question,
            choices,
            answer,
        )

        self.quizzes.append(new_quiz)

        if self.save_state():
            print("✅ 퀴즈가 추가되고 저장되었습니다!")

        else:
            print("⚠️ 퀴즈는 추가됐지만 파일 저장에는 실패했습니다.")

    def show_quiz_list(self):
        """등록된 퀴즈 목록을 출력한다."""

        print()

        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다.")
            return

        print(
            f"📋 등록된 퀴즈 목록 "
            f"(총 {len(self.quizzes)}개)"
        )
        print("-" * 40)

        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")

        print("-" * 40)

    def show_best_score(self):
        """최고 점수를 출력한다."""

        print()

        if self.best_total == 0:
            print("🏆 아직 퀴즈를 풀지 않았습니다.")
            return

        print(
            f"🏆 최고 점수: {self.best_score}점 "
            f"({self.best_total}문제 중 "
            f"{self.best_correct}문제 정답)"
        )

    def run(self):
        """종료를 선택할 때까지 메뉴를 반복한다."""

        try:
            while True:
                self.show_menu()

                menu_number = self.get_integer(
                    "선택: ",
                    1,
                    5,
                )

                if menu_number == 1:
                    self.play_quiz()

                elif menu_number == 2:
                    self.add_quiz()

                elif menu_number == 3:
                    self.show_quiz_list()

                elif menu_number == 4:
                    self.show_best_score()

                elif menu_number == 5:
                    self.save_state()
                    print("👋 프로그램을 종료합니다.")
                    break

        except (KeyboardInterrupt, EOFError):
            print()
            print(
                "⚠️ 입력이 중단되었습니다. "
                "데이터를 저장하고 종료합니다."
            )

            self.save_state()


if __name__ == "__main__": # python이 관리하는 name이 __main__ 모듈과 같은 경우 (직접실행시 아래 코드 실행)
    game = QuizGame()
    game.run()
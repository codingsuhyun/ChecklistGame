#이전에서 올라마의 실행방식을 바꿈
import tkinter as tk
from tkinter import messagebox
import random
import subprocess

# ollama 적 대사 생성

def generate_dialogue(prompt, model="llama2"):
    command = ["ollama", "run", model]
    try:
        result = subprocess.run(command, input=prompt, capture_output=True, text=True)
        if result.returncode == 0:
            response = result.stdout.strip()
            return response
        else:
            print("Error:", result.stderr)
            return None
    except Exception as e:
        print("Exception occurred:", str(e))
        return None

# 대사 프롬프트
myprompt = "Generate a short villainous line for an villain taking damage Within 20 characters."


# 초기 설정
user_hp = 10
enemy_hp = 5
enemy_level = 1
tasks = []

# 레벨별 적 체력 설정
LEVEL_HEALTH = {1: 5, 2: 5, 3: 5, 4: 5, 5: 5}

# UI 업데이트
def update_ui():
    user_hp_label.config(text=f"사용자 체력: {user_hp}")
    enemy_hp_label.config(text=f"적 체력: {enemy_hp} (레벨 {enemy_level})")

# 항목 추가
def add_task():
    global tasks
    task = task_entry.get()
    if task:
        attack_power = random.randint(1, 10)  # 공격력 1~10 랜덤
        tasks.append((task, attack_power, False))  # (작업명, 공격력, 완료여부)
        checklist.insert(tk.END, f"  {task} (공격력: {attack_power})")
        task_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("경고", "작업 내용을 입력하세요.")
    update_ui()

# 항목 완료
def complete_task():
    global enemy_hp
    selected = checklist.curselection()
    if not selected:
        messagebox.showwarning("경고", "완료할 작업을 선택하세요.")
        return
    index = selected[0]
    task, attack_power, _ = tasks[index]
    enemy_hp -= attack_power
    enemy_hp = max(0, enemy_hp)  # 체력이 음수로 가지 않도록 처리
    tasks[index] = (task, attack_power, True)  # 완료 처리
    checklist.delete(index)
    checklist.insert(index, f"✔ {task} (공격력: {attack_power})")
    update_ui()

    # 적 대사 생성
    dialogue = generate_dialogue(myprompt)

    # 메시지 창에 피해 메시지와 대사 출력
    messagebox.showinfo(
        "공격",
        f"적에게 {attack_power}만큼의 피해를 입혔습니다! 남은 체력: {enemy_hp}\n\n적의 한마디:{dialogue}"
    )

    if enemy_hp == 0:
        if enemy_level < 5:
            next_level()
        else:
            victory()

# 항목 실패
def fail_task():
    global user_hp
    selected = checklist.curselection()
    if not selected:
        messagebox.showwarning("경고", "수행하지 못한 작업을 선택하세요.")
        return
    index = selected[0]
    task, attack_power, _ = tasks[index]
    user_hp -= attack_power
    user_hp = max(0, user_hp)  # 체력이 음수로 가지 않도록 처리
    tasks[index] = (task, attack_power, False)  # 실패 처리
    checklist.delete(index)
    checklist.insert(index, f"✘ {task} (공격력: {attack_power})")
    update_ui()
    messagebox.showinfo("피격", f"일을 완수하지 못해 {attack_power}만큼의 피해를 입었습니다! 남은 체력: {user_hp}")
    if user_hp == 0:
        game_over()

# 항목 삭제
def delete_selected_task():
    global tasks
    selected = checklist.curselection()
    if not selected:
        messagebox.showwarning("경고", "삭제할 작업을 선택하세요.")
        return
    index = selected[0]
    del tasks[index]
    checklist.delete(index)

# 전체 항목 삭제
def delete_all_tasks():
    global tasks
    tasks.clear()
    checklist.delete(0, tk.END)

# 다음 레벨로 이동
def next_level():
    global enemy_hp, enemy_level, user_hp
    def proceed():
        global user_hp, enemy_hp, enemy_level
        user_hp = 100
        enemy_level += 1
        enemy_hp = LEVEL_HEALTH[enemy_level]
        update_ui()
        next_level_popup.destroy()

    next_level_popup = tk.Toplevel(root)
    next_level_popup.title("적 처치!")
    next_level_popup.geometry("300x150")
    tk.Label(next_level_popup, text=f"레벨 {enemy_level}의 적을 처치했습니다!", font=("Arial", 14)).pack(pady=10)
    next_level_button = tk.Button(next_level_popup, text="다음 단계로 이동", command=proceed)
    next_level_button.pack(pady=20)

# 최종 승리 처리
def victory():
    global enemy_level
    def retry():
        global user_hp, enemy_hp, enemy_level
        user_hp = 100
        enemy_level = 1
        enemy_hp = LEVEL_HEALTH[enemy_level]
        update_ui()
        victory_popup.destroy()

    victory_popup = tk.Toplevel(root)
    victory_popup.title("최종 승리!")
    victory_popup.geometry("300x150")
    tk.Label(victory_popup, text="레벨 5의 보스를 처치했습니다!", font=("Arial", 14)).pack(pady=10)
    retry_button = tk.Button(victory_popup, text="Retry", command=retry)
    retry_button.pack(pady=20)

# 게임 오버 처리
def game_over():
    global enemy_level
    def retry():
        global user_hp, enemy_hp, enemy_level
        user_hp = 100
        enemy_level = 1
        enemy_hp = LEVEL_HEALTH[enemy_level]
        update_ui()
        game_over_popup.destroy()

    game_over_popup = tk.Toplevel(root)
    game_over_popup.title("패배")
    game_over_popup.geometry("300x150")
    tk.Label(game_over_popup, text="사용자가 사망했습니다!", font=("Arial", 14)).pack(pady=10)
    retry_button = tk.Button(game_over_popup, text="Retry", command=retry)
    retry_button.pack(pady=20)

# GUI 생성
root = tk.Tk()
root.title("체크리스트 게임")
root.geometry("800x320")

# 상단: 체력 정보
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

user_hp_label = tk.Label(top_frame, text=f"사용자 체력: {user_hp}", font=("Arial", 12))
user_hp_label.pack(side=tk.LEFT, padx=20)

enemy_hp_label = tk.Label(top_frame, text=f"적 체력: {enemy_hp} (레벨 {enemy_level})", font=("Arial", 12))
enemy_hp_label.pack(side=tk.RIGHT, padx=20)

# 중앙: 체크리스트와 입력 필드
main_frame = tk.Frame(root)
main_frame.pack()

# 체크리스트
checklist = tk.Listbox(main_frame, width=40, height=15)
checklist.pack(side=tk.LEFT, padx=10)

# 입력 필드와 버튼
control_frame = tk.Frame(main_frame)
control_frame.pack(side=tk.RIGHT)

task_entry = tk.Entry(control_frame, width=30)
task_entry.grid(row=0, column=0, padx=5, pady=5)

add_button = tk.Button(control_frame, text="작업 추가", command=add_task)
add_button.grid(row=0, column=1, padx=5)

complete_button = tk.Button(control_frame, text="완료", command=complete_task)
complete_button.grid(row=1, column=0, columnspan=2, pady=5)

fail_button = tk.Button(control_frame, text="실패", command=fail_task)
fail_button.grid(row=2, column=0, columnspan=2, pady=5)

delete_selected_button = tk.Button(control_frame, text="선택 항목 삭제", command=delete_selected_task)
delete_selected_button.grid(row=3, column=0, columnspan=2, pady=5)

delete_all_button = tk.Button(control_frame, text="전체 항목 삭제", command=delete_all_tasks)
delete_all_button.grid(row=4, column=0, columnspan=2, pady=5)

# UI 초기화
update_ui()

# 메인 루프 실행
root.mainloop()
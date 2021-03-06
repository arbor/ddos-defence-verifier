my_ip = '0.0.0.0' # Listening Local IP for DDV-TG-x. Modify manually on each TG Agent
ddv_c_ip = '255.255.255.255' # Autodetected DDV console server IP (Specify the real IP if your DDV Console Server)
ddv_tg_v_port = 1980 # TCP listener port for Verrifier Traffic Generator
ddv_tg_a_port = 1981 # TCP listener port for Attacker Traffic Generator
ddv_v_enrollment_filename = 'ddv_tg_v_enrollment.csv' # Verifier enrollment data
ddv_a_enrollment_filename = 'ddv_tg_a_enrollment.csv' # Attacker enrollment data
ddv_tg_v_task_filename = 'ddv_tg_v_task.csv' # Verifier traffic generator tasks data
ddv_tg_v_task_pid_filename = 'ddv_tg_v_task_pid.csv' # Verifier traffic generator tasks PID data
ddv_tg_a_task_filename = 'ddv_tg_a_task.csv' # Attacker traffic generator tasks data
ddv_tg_a_task_pid_filename = 'ddv_tg_a_task_pid.csv' # Attacker traffic generator tasks PID data
ddv_tg_v_tasks_run_int = 1 # sec interval between running verifier traffic generator tests
ddv_tg_a_tasks_run_int = 1 # sec interval between running attack traffic generator tests

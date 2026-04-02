"""
create_schedule.bat - 创建 Windows 定时任务（每日 22:00）
配合 cron_job.py 使用
"""
import subprocess
import sys

TASK_NAME = "valuation_grid_daily"
BATCH_FILE = r"E:\Git\valuation_grid\run_cron.bat"
LOG_FILE = r"E:\Git\valuation_grid\cron_log.txt"

def create_schedule():
    """创建定时任务（每日 22:00）"""
    cmd = [
        "schtasks",
        "/create",
        "/tn", TASK_NAME,
        "/tr", f'"{BATCH_FILE}"',
        "/sc", "daily",
        "/st", "22:00",
        "/f"  # 覆盖已存在任务
    ]
    
    print(f"Creating task: {TASK_NAME}")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk')
    
    if result.returncode == 0:
        print("[OK] Task created successfully!")
        print(result.stdout)
        return True
    else:
        print("[FAIL] Failed to create task:")
        print(result.stderr)
        return False

def test_run():
    """立即运行一次测试"""
    cmd = ["schtasks", "/run", "/tn", TASK_NAME]
    print("Running task for testing...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk')
    if result.returncode == 0:
        print("[OK] Task started successfully!")
        print(result.stdout)
    else:
        print("[FAIL] Failed to run task:")
        print(result.stderr)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_run()
    else:
        create_schedule()

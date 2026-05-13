import time
from core.blockchain import proof_of_work

def test_pow_performance():
    """性能测试：验证 PoW 耗时"""
    difficulty = 4
    last_proof = 100
    
    start_time = time.time()
    proof = proof_of_work(last_proof, difficulty)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"\n[PERF] Difficulty {difficulty} PoW took: {duration:.4f}s")
    assert proof > 0
    # 难度 4 通常在 1秒内完成
    assert duration < 5.0

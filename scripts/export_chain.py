import json
import os
from web import create_app
from db.models import Block

app = create_app()


def export_to_json(output_path="backup/chain_data.json"):
    with app.app_context():
        blocks = Block.query.order_by(Block.index.asc()).all()
        chain_data = []
        for b in blocks:
            chain_data.append({
                "index": b.index, "timestamp": b.timestamp,
                "transactions": json.loads(b.transactions),
                "proof": b.proof, "previous_hash": b.previous_hash,
                "hash": b.hash, "difficulty": b.difficulty
            })

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chain_data, f, indent=4)
        print(f"✅ 成功导出 {len(blocks)} 个区块到 {output_path}")


if __name__ == "__main__":
    export_to_json()
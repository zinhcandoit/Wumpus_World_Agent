# Wumpus World Agent

Tác tử Wumpus World với suy luận mệnh đề, KB động theo bước thời gian, cắt tỉa tri thức theo bán kính, và Wumpus di chuyển định kỳ. Chạy nhanh, dễ mở rộng, có giải thích từng phần.

## Điểm nổi bật

- **Mô hình tri thức theo thời gian**: Literal có `at_step` để reset tri thức khi Wumpus thay đổi hoặc di chuyển
- **Suy luận TT-Entails**: Kiểm tra hệ mệnh đề theo Truth Table với cắt nhánh khi clause mâu thuẫn
- **Cắt tỉa tri thức**: Giữ tri thức tĩnh và clause gần agent để giảm không gian tìm kiếm
- **Quyết định cục bộ**: Xây focus set cho các ô quan trọng và tia bắn
- **Wumpus động**: Cứ 5 bước Wumpus di chuyển ngẫu nhiên, tránh pit và tránh đè nhau
- **Hệ thống điểm**: +1000 khi climb out có vàng, −1 cho di chuyển/quay, −10 cho bắn, +10 cho grab, −1000 khi chết

## Kiến trúc code

```
Development/
  ├─ definition.py   # Literal có at_step, so khớp, hash
  ├─ agent.py        # Agent, cập nhật KB từ percepts, chọn action
  ├─ algorithm.py    # TT-entails, prune_by_radius, focus set, chọn action
  ├─ map.py          # Sinh bản đồ, percepts, Wumpus move mỗi 5 bước
  └─ gameState.py    # Vòng lặp chơi, tính điểm, dừng game
```

## Cách chạy

Yêu cầu Python 3.10+

```bash
git clone https://github.com/zinhcandoit/Wumpus_World_Agent
cd Wumpus_World_Agent
pip install -r requirements.txt
```

Chạy thử một game:

```python
from Development.gameState import Game

game = Game(size=4, pit_density=0.2, num_wumpus=2)
score, actions, w_hist = game.play()
print("Score:", score)
print("Actions:", actions)
print("Wumpus histories:", w_hist)
```

## Cách hoạt động

1. Agent nhận percepts từ map (`glitter/stench/breeze/scream`)
2. Percepts được chuyển thành clause và thêm vào KB
3. KB được cắt tỉa theo bán kính quanh agent
4. Dựng focus set để kiểm tra an toàn/không an toàn
5. Entailment cho từng literal trong focus → quyết định hành động
6. Wumpus di chuyển mỗi 5 bước, lịch sử được ghi lại
7. Điểm số được cập nhật theo action

## Bảng phân công

| Member           | Student ID | Role                                         | Key task                                                                                                                                                                                                                     | Overall Contribution |
| ---------------- | ---------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| Thieu Quang Vinh | 23127143   | Game system design; baseline random strategy | 1) Define game architecture and state flow.<br>2) Implement random action policy and integration with scoring.<br>3) Wire percept→KB hooks in the main loop.<br>4) Draft core system sections of the report.                 | 100%                 |
| Tran Hai Duc     | 23127173   | UI/UX and evaluation framework               | 1) Build UI components (Text, Button, Slider) and screens.<br>2) Render solver outputs on GameScreen.<br>3) Implement comparison harness and metrics (success rate, avg length).<br>4) Write the report except Sections 4–5. | 100%                 |
| Pham Thanh Loc   | 23127405   | Heuristic planner (A\* for pathfinding)      | 1) Implement logic/heuristic strategy with A\* (cost, heuristic, tie-breaking) and integrate with choose_action("logic").<br>2) Write report part 5.                                                                         | 100%                 |

## License

MIT License

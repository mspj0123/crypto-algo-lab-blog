---
layout: post
title: "[hybrid_boost_trader] トレンドフィルター 4h→2h EMA200 変更"
date: 2026-05-01
notion_id: 3548f0b7-804f-816d-bc70-dcf898801b8d
categories: [実装]
tags: []
---

- トレンドフィルターを 4h EMA200 → 2h EMA200 に変更
- config.EMA_TREND_TFで足種を一元管理（将来的に1行で切り替え可能）
- fetch_trend_ohlcv()を新設しflexibleな足種取得に対応
---

- 4h EMA200（旧）: 取引14件 勝率50.0% +15,975円 PF1.99
- 2h EMA200（採用）: 取引19件 勝率73.7% +41,863円 PF3.32  ← +2.6倍のパフォーマンス
- 1h EMA200: 取引24件 勝率58.3% +41,447円 PF2.97
- フィルターなし: 取引49件 勝率61.2% +151,912円 PF4.44（リスク高）
2h EMA200が勝率・PF・損益のバランス最良。4hより取引機会が35%増加。


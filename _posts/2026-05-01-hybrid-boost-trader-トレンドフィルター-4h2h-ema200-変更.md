---
layout: post
title: "[hybrid_boost_trader] トレンドフィルター 4h→2h EMA200 変更"
date: 2026-05-01
categories: [実装]
tags: []
---

## 📋 変更概要

- トレンドフィルターを 4h EMA200 → 2h EMA200 に変更
- config.EMA_TREND_TFで足種を一元管理（将来的に1行で切り替え可能）
- fetch_trend_ohlcv()を新設しflexibleな足種取得に対応
---

## 📊 バックテスト比較結果（過去3ヶ月）

### フィルター別成績

- 4h EMA200（旧）: 取引14件 勝率50.0% +15,975円 PF1.99
- 2h EMA200（採用）: 取引19件 勝率73.7% +41,863円 PF3.32  ← +2.6倍のパフォーマンス
- 1h EMA200: 取引24件 勝率58.3% +41,447円 PF2.97
- フィルターなし: 取引49件 勝率61.2% +151,912円 PF4.44（リスク高）
2h EMA200が勝率・PF・損益のバランス最良。4hより取引機会が35%増加。

---

## 🔧 変更ファイル

- src/config.py — EMA_TREND_TF = "2h" 追加
- src/data/coincheck_client.py — 2h足リサンプル対応追加
- src/data/market_data.py — fetch_trend_ohlcv() 新設
- src/strategy/entry.py — ログメッセージを動的化
- main.py — fetch_4h_ohlcv → fetch_trend_ohlcv に変更
---

## ⏭ 次のアクション

- 2h EMA200設定で2週間以上の実運用データを蓄積して効果を検証
- 必要に応じてMLフィルター閾値（現在0.55）の再調整を検討

---

*本記事は技術的な実装紹介を目的としており、投資を推奨するものではありません。*

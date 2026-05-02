---
layout: post
title: "[hybrid_boost_trader] MLフィルター統合・大型通貨絞り込み・ダッシュボード改善"
date: 2026-04-30
notion_id: 3548f0b7-804f-81be-835e-c2e9a46668de
categories: [実装]
tags: []
---

- 対象ペアを9ペア→5ペア（BTC/ETH/XRP/SOL/AVAX）に絞り込み
- LightGBM MLフィルターを実装（勝率向上: 87.5%、PF 7.98）
- ダッシュボードの保有資産内訳を対象通貨のみにフィルタリング
---

- MLフィルター特徴量15個・LightGBM設計は適切
- 週次再学習による概念ドリフト対応も良い
- 軽微指摘: yfinance↔Coincheckデータ乖離（実用上問題なし）
### Mark Minervini（リスク管理）


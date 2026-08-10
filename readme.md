# TCG Radar

TCG Radar is a personal research tool for collecting and analyzing public discussion around trading card game products.

The goal is to reduce the amount of manual research required to follow upcoming releases, market sentiment, supply concerns, restocks, and product demand across multiple TCG communities.

## Current Status

TCG Radar is an early development prototype.

The current version supports YouTube-based market research and contains the infrastructure for future Reddit integration.

## Supported TCGs

Current monitoring is designed around major trading card games including:

- Pokémon TCG
- Magic: The Gathering
- Disney Lorcana
- One Piece Card Game
- Yu-Gi-Oh!
- Flesh and Blood
- Star Wars: Unlimited
- Digimon Card Game
- Riftbound

Additional games and search terms can be added through `settings.json`.

## YouTube Research

The YouTube collector can discover recent videos related to:

- new releases
- upcoming sets
- preorders
- restocks
- market discussion
- product demand
- investing/collecting discussion

Discovered videos are stored locally in an SQLite database.

TCG Radar can then retrieve public comments from those videos and analyze market-related language.

Examples of signals currently being detected include:

- buying intent
- hype
- supply shortages
- restocks
- products considered overpriced
- products considered undervalued
- expectations of increasing prices
- expectations of decreasing prices
- people waiting or skipping products

The project is also being developed toward product-level analysis so that signals can be associated with specific sets, cards, and sealed products rather than only entire TCGs.

## Reddit Integration

Reddit Data API access has been requested.

The planned Reddit integration is read-only.

The application is intended to retrieve public posts and comments from selected TCG-related subreddits and analyze discussion patterns across them.

The application will not:

- create posts
- create comments
- vote
- send messages
- contact users
- perform moderation actions

Reddit data will be used as an additional research signal alongside other public TCG information sources.

## Architecture

The current system is structured roughly as:

YouTube discovery  
→ local database  
→ comment collection  
→ market-language analysis  
→ product/topic analysis  
→ TCG Radar report

Future sources such as Reddit can feed into the same analysis pipeline.

## Project Files

- `tcgradar.py` — main program/controller
- `youtube_collector.py` — discovers relevant YouTube videos
- `youtube_comments.py` — retrieves public comments from saved videos
- `youtube_database.py` — stores YouTube information locally
- `youtube_analyzer.py` — analyzes market-related language
- `product_analyzer.py` — identifies product/topic-level signals
- `database.py` — local database utilities
- `analyzer.py` — general analysis functions
- `trends.py` — trend detection
- `settings.json` — editable monitoring settings

## Privacy and Credentials

API credentials are stored locally in `.env`.

The `.env` file and local SQLite database are excluded from the public repository through `.gitignore`.

API keys and private credentials should never be committed to this repository.

## Disclaimer

TCG Radar is an experimental research project.

Its signals are not financial advice and are not predictions of future product or card prices.
---
name: jellyfin-media-naming
description: Name and file finished movies and TV series for a Jellyfin library in the owner's style (English title + Hong Kong Chinese title + year + tags). Use when naming, renaming or moving converted movies or series episodes into the library, or choosing a Hong Kong title.
---

# Jellyfin media naming

Rules derived (read-only) from the owner's library on 2026-11-28: movies in one flat folder (about 1,385 entries), series in `<drama root>\<region>\<Title [Year]>\Season NN\`. Paths such as `Y:\movies` are examples.

Done = every file has a name from the pattern below whose Chinese title is confirmed from a source (or marked unconfirmed in the report), and `scripts/plan_moves.py` dry-run shows no refusal.

## Movie pattern

`<English title> <Hong Kong Chinese title> [<year>] [<tag>] ... .<ext>`

Real examples from the library: `Batman Begins 蝙蝠俠—俠影之謎 [2005] [4K].mp4` (the owner's reference file), `X-Men： Apocalypse 變種特攻 ： 天啟滅世戰 [2016] [4K].mp4`, `Blacklight 黑殺潛行 [2022] [4K] [HDR].mkv`, `The Wolverine 狼人：武士激戰 [2013] [加長版].mkv`, `Ghostbusters 捉鬼敢死隊 2016 [2016] [720p].mkv`.

- Space between the English and Chinese title, no separator. The year is always `[yyyy]`.
- **ASCII `:` in a title becomes full-width `：`** (Windows forbids `:`); also avoid `< > " / \ | ? *`.
- **Remake**: the year is repeated after the Chinese title (`捉鬼敢死隊 2016 [2016]`) so it differs from the original.
- **Tags** (only when they apply): resolution when not 1080p (`[4K]`, `[720p]`, `[576p]`, `[480p]`, `[SD]`), edition (`[加長版]`), `[HDR]`, audio language such as `[國語]`. Resolution comes first, `[HDR]` after it. Order of edition vs resolution is not settled by the library (no file has both): this skill uses edition then resolution (`[2016] [加長版] [4K]`); confirm with the owner when it matters.
- Subtitles: `<same stem>.zh-TW.srt` (also `.en.srt`, `.zh-CN.srt`). Multi-part files: `-cd1`, `-cd2` after the tags.
- Converted discs from the `iso-to-mp4` skill are UHD, so they carry `[4K]`.

## Chinese title = the Hong Kong release title, Traditional characters

Not the mainland or Taiwan title: 猩球崛起 (mainland) is `猿人爭霸戰：猩凶革命` here. Lookup order, stop at the first hit:

1. An existing file of the same film or franchise in the library (`ls` the movies folder for the English title).
2. zh.wikipedia infobox / article, 香港譯名 field.
3. TMDB `zh-HK` translation.

Anything not confirmed from one of these is **unconfirmed**: say so in the report, never present a guess as fact.

## Worked examples (chosen 2026-11-28, all UHD, same shape as the Batman Begins reference)

| Film | File name |
|---|---|
| Ghostbusters (1984) | `Ghostbusters 捉鬼敢死隊 [1984] [4K].mp4` |
| Ghostbusters II | `Ghostbusters II 捉鬼敢死隊 2 [1989] [4K].mp4` |
| Ghostbusters (2016, extended) | `Ghostbusters 捉鬼敢死隊 2016 [2016] [加長版] [4K].mp4` |
| Rise of the Planet of the Apes | `Rise of the Planet of the Apes 猿人爭霸戰：猩凶革命 [2011] [4K].mp4` |
| Dawn of the Planet of the Apes | `Dawn of the Planet of the Apes 猿人爭霸戰：猩凶崛起 [2014] [4K].mp4` |
| Logan | `Logan 盧根 [2017] [4K].mp4` |
| Men in Black | `Men in Black 黑超特警組 [1997] [4K].mp4` |
| Men in Black II | `Men in Black II 黑超特警組 2 [2002] [4K].mp4` |
| Men in Black 3 | `Men in Black 3 黑超特警組 3 [2012] [4K].mp4` |

## TV series and multi-episode discs

Layout: `<drama root>\<region>\<Title [Year]>\Season NN\<Title> - SNNEMM.mp4`, regions `台劇 國劇 日劇 歐美劇 港劇 韓劇`. Example: `Star Wars： Visions 星球大戰：幻境 [2021]\Season 01\星球大戰：幻境 - S01E01.mp4` (this one sits directly under the drama root, no region folder: an exception in the library).

A disc holding several episodes needs `SNNEMM` per file, or one multi-episode file `<Title> - S01E01-E02.mp4`. **The mapping disc -> episodes comes from the disc (titles / chapters) or from the owner. Never guess it**; if neither is available, stop and ask with the list of titles the disc contains.

## Radarr assessment (not used)

Source: Servarr wiki `radarr/settings.md` (raw.githubusercontent.com/Servarr/Wiki/master/radarr/settings.md). Tokens: `{Movie Title}`, `{Movie Title:XX}` (per-language, e.g. `:DE`), `{Movie CleanTitle}`, `{Movie OriginalTitle}`. No documented Chinese variant (zh-HK vs zh-CN). The colon "Smart Replace" turns `: ` into ` - `, the library uses `：`. It renames an existing library only after importing it into a running Radarr server. Verdict: not used (one language per token, no confirmed HK variant, a server to run for a one-off rename); revisit only if the owner wants automated downloading. Unicode itself is not a documented problem.

## Moving files

`scripts/plan_moves.py --map moves.json --converted-dir <dir> --trash-dir <dir> --manifest moves.jsonl` (dry run; add `--apply`). Mapping rows: `mp4`, `name`, optional `folder`. It renames on the same drive only, refuses overwrites, refuses to trash a folder that still holds an unconverted disc, and writes a JSONL manifest; `--undo moves.jsonl --apply` reverses it.

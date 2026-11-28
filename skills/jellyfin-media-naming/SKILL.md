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
| Men in Black: International | `Men in Black： International 黑超特警組：全球特攻 [2019] [4K].mp4` (HK title unconfirmed) |
| The Hunger Games (+ extras disc) | `The Hunger Games 飢餓遊戲 [2012] [4K].mp4` + `The Hunger Games 飢餓遊戲 [2012] [4K]-behindthescenes.mp4` |
| The Hunger Games: Catching Fire | `The Hunger Games： Catching Fire 飢餓遊戲 2：星火燎原 [2013] [4K].mp4` (zh.wikipedia) |
| Kingsman: The Secret Service | `Kingsman： The Secret Service 皇家特工：間諜密令 [2014] [4K].mp4` (unconfirmed) |
| The Mummy (1999) | `The Mummy 盜墓迷城 [1999] [4K].mp4` (zh.wikipedia) |
| The Mummy Returns | `The Mummy Returns 盜墓迷城 2 [2001] [4K].mp4` (zh.wikipedia) |
| The Mummy: Tomb of the Dragon Emperor | `The Mummy： Tomb of the Dragon Emperor 盜墓迷城 3 [2008] [4K].mp4` (unconfirmed) |
| The Mummy (2017 remake) | `The Mummy 盜墓迷城 2017 [2017] [4K].mp4` (zh.wikipedia) |
| War for the Planet of the Apes | `War for the Planet of the Apes 猿人爭霸戰：猩凶巨戰 [2017] [4K].mp4` (zh.wikipedia; NOT 猩凶終結, a first guess that was wrong) |
| Spider-Man: Across the Spider-Verse (1080p source) | `Spider-Man： Across the Spider-Verse 蜘蛛俠：飛越蜘蛛宇宙 [2023].mp4` (no `[4K]`: not UHD; HK title unconfirmed) |

A guessed HK title can be confidently wrong (猩凶終結 vs the real 猩凶巨戰): look every one up, and list the unconfirmed ones to the owner.

## TV series and multi-episode discs

Layout: `<drama root>\<region>\<Title [Year]>\Season NN\<Title> - SNNEMM.mp4`, regions `台劇 國劇 日劇 歐美劇 港劇 韓劇`. Example: `Star Wars： Visions 星球大戰：幻境 [2021]\Season 01\星球大戰：幻境 - S01E01.mp4` (this one sits directly under the drama root, no region folder: an exception in the library).

Second reference from the owner: `Y:\drama\國劇\周生如故 [2021]\Season 01\周生如故 - S01E01 [720p].mp4` (resolution tag after the episode).

A disc holding several episodes needs `SNNEMM` per file, or one multi-episode file `<Title> - S01E01-E02.mp4`. **The mapping disc -> episodes comes from the disc (titles / chapters) or from the owner. Never guess it**; if neither is available, stop and ask with the list of titles the disc contains.

**Owner rule (2026-11-28, "一隻碟一個檔")**: when the episode mapping is unknown, a DVD series is filed one file per disc, disc N = `SNNEMM` with MM = N: `命中注定我愛你 [2008]\Season 01\命中注定我愛你 - S01E01 [480p].mp4` ... `S01E10` for 碟一..碟十. Title in Traditional characters (source folder said 命中注定我爱你).

## What Jellyfin itself documents (checked 2026-11-28, jellyfin.org docs + naming source)

- TV: `Series (year)\Season 01\Series S01E01.ext`; a multi-episode file `S01E01-E03`. Our `[2021]` year in brackets is accepted by Jellyfin's CleanDateTimes regex (read from the regex only, not tested in a running server).
- Movies: the docs recommend one folder per movie; the owner's flat movies folder is not documented, it works in their library today. Do not restructure it unasked.
- Extras: suffix `-behindthescenes` (also `-trailer`, `-featurette`, `-deleted`, ...) on the same stem as the movie.

## Radarr assessment (not used)

Source: Servarr wiki `radarr/settings.md` (raw.githubusercontent.com/Servarr/Wiki/master/radarr/settings.md). Tokens: `{Movie Title}`, `{Movie Title:XX}` (per-language, e.g. `:DE`), `{Movie CleanTitle}`, `{Movie OriginalTitle}`. No documented Chinese variant (zh-HK vs zh-CN). The colon "Smart Replace" turns `: ` into ` - `, the library uses `：`. It renames an existing library only after importing it into a running Radarr server. Verdict: not used (one language per token, no confirmed HK variant, a server to run for a one-off rename); revisit only if the owner wants automated downloading. Unicode itself is not a documented problem.

## Moving files

`scripts/plan_moves.py --map moves.json --converted-dir <dir> --trash-dir <dir> --manifest moves.jsonl` (dry run; add `--apply`). Mapping rows: `mp4`, `name`, optional `folder`. It renames on the same drive only, refuses overwrites, refuses to trash a folder that still holds an unconverted disc, and writes a JSONL manifest; `--undo moves.jsonl --apply` reverses it.

Gaps found 2026-11-28 (work around them, do not fight the guard):
- **"Converted" means the disc's own `<iso stem>.mp4` is in the mapping.** A repaired or re-joined file with another name (`x.mp4.fix.partial`) is refused as "unconverted": first rename the old output aside (`.mp4.v1`) and the new one to `<stem>.mp4`, then map that.
- **`--trash-dir` is the parent**: a folder keeps its own name inside it (`--trash-dir to-be-removed\X` gives `to-be-removed\X\<folder>`, nested). Always pass the plain `to-be-removed`.
- **It moves whole folders only.** A multi-disc folder that is partly done (9 of 10 DVDs converted) cannot be parked; move the finished ISOs by hand with a logged loop (append the same JSON lines to the manifest) and park the folder when the last disc is done.
- **`name` is a bare file name** (no subfolder). For a series, create `<Title [Year]>\Season 01` yourself and pass that as `--converted-dir` for those rows.
- **Never delete `to-be-removed`**: the owner checks the outputs and deletes it themselves.

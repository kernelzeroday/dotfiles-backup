# Expand Subversive Quotes Database — Design

## Goal

Roughly double the quote database from ~1,360 quotes / 209 figures / 23 categories to ~2,500-2,800 quotes / ~350-400 figures / 27 categories. Stay focused on the theme: powerful and subversive figures who challenged power structures, spoke truth to power, or operated in the shadows of established systems.

## New Categories (4)

| Category | Theme | Target size |
|---|---|---|
| Hackers & Cypherpunks | Digital freedom, crypto, open information, hacker ethos | 10-15 figures, 5-8 quotes each |
| Activists & Dissidents | Civil disobedience, protest movements, anti-war, civil rights | 10-15 figures, 5-8 quotes each |
| Economists & Economic Dissidents | Challenged economic orthodoxies, critiqued capitalism/inequality | 10-15 figures, 5-8 quotes each |
| Revolutionaries & Guerrillas | Armed revolution, insurgency, overthrowing regimes | 10-15 figures, 5-8 quotes each |

Example figures per new category:
- **Hackers & Cypherpunks:** Aaron Swartz, Richard Stallman, Tim Berners-Lee, Moxie Marlinspike, Phil Zimmermann, John Perry Barlow, Whitfield Diffie, Eric S. Raymond, Linus Torvalds, Edward Snowden
- **Activists & Dissidents:** MLK Jr, Malcolm X, Mahatma Gandhi, Rosa Parks, Cesar Chavez, Frederick Douglass, Aung San Suu Kyi, Nelson Mandela, Harvey Milk, Emma Goldman, Angela Davis, Susan B. Anthony
- **Economists & Economic Dissidents:** Karl Marx, John Maynard Keynes, Friedrich Hayek, Adam Smith, Amartya Sen, Naomi Klein, Thomas Piketty, Milton Friedman, John Kenneth Galbraith, Thorstein Veblen
- **Revolutionaries & Guerrillas:** Che Guevara, Emiliano Zapata, Leon Trotsky, Subcomandante Marcos, Toussaint Louverture, Simon Bolivar, Giuseppe Garibaldi, Michael Collins

## Existing Categories — Expansion Targets

Thin categories get the most attention (target ~55-65 quotes each):
- Intelligence Figures: 25 → 60
- Whistleblowers & Spies: 23 → 60
- Media & Propaganda: 28 → 55
- Latin American Leaders: 30 → 55
- Middle Eastern Leaders: 31 → 55
- Chinese Leaders: 34 → 55
- Military Leaders: 34 → 55
- Ancient & Medieval Rulers: 37 → 65
- African Leaders: 41 → 55
- Secret Societies: 42 → 55
- European Leaders: 43 → 55

Well-covered categories get modest additions of overlooked subversive voices:
- US Politicians (212), International Leaders (112), Tech Leaders (107), Russian Leaders (86), Business Leaders (73), Artists & Writers (71), Philosophers (67), Scientists (60), Conspiracy & Alternative Figures (51), Religious & Ideological Figures (48), Historical Figures (47), US Adversaries (58)

## Implementation Approach

### What changes
- `data/quotes.json` — all new quotes and figures
- `README.md` — updated counts

### No code changes
The Rust CLI, database schema, and all APIs remain identical. New quotes use the same `{figure, text, category}` structure.

### Method
Write a Python merge script (`scripts/merge_quotes.py`) that:
1. Reads the current `quotes.json`
2. Defines new quotes inline as Python data structures
3. Validates for duplicate (figure, text) pairs and schema consistency
4. Serializes the merged database back to `quotes.json`

Batched into 7 chunks for manageable context and review:
1. New category: Hackers & Cypherpunks
2. New category: Activists & Dissidents
3. New category: Economists & Economic Dissidents
4. New category: Revolutionaries & Guerrillas
5. Expand thin categories (phase 1)
6. Expand thin categories (phase 2)
7. Modest additions to well-covered categories + README update

### Validation
- `cargo test` after each batch to verify the database loads and tests pass
- `subversive stats` after completion to confirm final counts

# Rozkład grafu K₅₆₁ na kopie K₁₁

**Zadanie dodatkowe z teorii grafów – Problem dekompozycji grafu pełnego**

---

## Opis problemu

Zadanie polega na znalezieniu rozkładu grafu pełnego K₅₆₁ na jak największą liczbę rozłącznych krawędziowo klik K₁₁. Każda krawędź grafu musi należeć do dokładnie jednej kliki K₁₁.

Graf K₅₆₁ ma 157080 krawędzi, a każda klika K₁₁ zawiera 55 krawędzi, więc pełny rozkład wymagałby dokładnie 2856 bloków. 

Wierzchołki zostały podzielone na 51 grup po 11 elementów, które tworzą 51 bazowych klik wewnątrzgrupowych. Celem programu jest znalezienie jak największej liczby **klik krzyżowych**.

**Główny cel projektu:** przekroczenie 2000 bloków łącznie (klik krzyżowych + 51 bloków bazowych).

---

## Algorytm

Program łączy metodę zachłanną (Greedy) z zaawansowanym lokalnym przeszukiwaniem. Wykorzystuje bitową reprezentację grafu, backtracking oraz mechanizm Simulated Annealing.

W fazie Greedy budowana jest solidna baza startowa. Gdy algorytm utknie, uruchamiany jest tryb luźny. W fazie Local Search program agresywnie usuwa dużą liczbę klik (120–350), a następnie próbuje odbudować fragment grafu w lepszy sposób. Mechanizm Simulated Annealing pozwala na chwilowe akceptowanie gorszych rozwiązań, aby uniknąć utknięcia w lokalnym minimum.

Program regularnie zapisuje najlepsze rozwiązanie co 5 minut oraz na samym końcu.

---

## Struktura plików

```bash
.
├── decompose_k561.py              # Główny kod programu
└── README.md


Wymagania i uruchomienie

Python 3.8 lub nowszy
Brak zewnętrznych bibliotek


Uruchomienie:
python decompose_k561.py


Plik najlepsze_rozwiazanie.txt
Plik zawiera wyłącznie kliki krzyżowe. Każda linia to jedna klika K₁₁ – dokładnie 11 liczb (numerów wierzchołków od 0 do 560), posortowanych rosnąco i oddzielonych spacjami.
0 12 25 37 48 61 73 89 102 115 130
1 15 28 39 52 64 77 90 104 118 133


Oczekiwane wyniki
| Etap        | Czas orientacyjny | Oczekiwana liczba klik krzyżowych |
|-------------|------------------|------------------------------------|
| Greedy      | 3–5 minut        | 1480–1580                          |
| Local Search| 40–90 minut      | +450–700                           |
| **Razem**   | 40–100 minut     | **1950–2200+**                     |


Uwagi

Wynik jest losowy – zmiana random.seed() w kodzie generuje inne rozwiązania.
Program automatycznie weryfikuje poprawność rozwiązania na końcu.
Im dłużej działa Local Search, tym lepszy wynik.


Parametry konfiguracyjne algorytmu

#### Deterministyczność
- `random.seed(54321)` — ustawiany w `main()`, kontroluje powtarzalność wyników  
  Zalecane: `123`, `777`, `999`, `320`

#### Budżety czasowe
- Greedy phase: `320s` (okno: 300–400s)
- Całkowity runtime: `7200s` (typowo 1–3h)

#### Ekspansja lokalna
- `trials = 55` — liczba prób znalezienia kliki (zalecane: 40–70)
- usuwanie klik na iterację: `120–350` (im więcej, tym bardziej agresywna eksploracja)

#### Simulated Annealing
- `temperature = 130.0` — początkowa eksploracja (80–150)
- `cooling rate = 0.989` — tempo schładzania (0.985–0.995)"# graph-decomposition-k561" 
"# graph-decomposition-k561" 

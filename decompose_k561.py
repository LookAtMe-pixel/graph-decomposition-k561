import random
import time

N = 561
GROUPS = 51
SIZE = 11
K = 11
TOTAL_EDGES = N * (N - 1) // 2
INSIDE_BLOCKS = 51

allmask = (1 << N) - 1
group_masks = []
for g in range(GROUPS):
    mask = 0
    for a in range(SIZE):
        mask |= 1 << (g * SIZE + a)
    group_masks.append(mask)


def init_cross_adj():
    adj = [0] * N
    deg = [N - SIZE] * N
    for v in range(N):
        g = v // SIZE
        adj[v] = allmask ^ group_masks[g]
    return adj, deg


def remove_clique(adj, deg, C):
    for i, v in enumerate(C):
        for w in C[i + 1:]:
            adj[v] &= ~(1 << w)
            adj[w] &= ~(1 << v)
            deg[v] -= 1
            deg[w] -= 1


def random_edge_high(adj, deg):
    candidates = [v for v in range(N) if deg[v] > 6]
    if not candidates:
        candidates = [v for v in range(N) if deg[v] > 0]
    if not candidates:
        return None

    v = max(candidates, key=lambda x: (deg[x], random.random() * 70))
    x = adj[v]
    if x == 0:
        return None

    opts = []
    for _ in range(300):
        w = random.randrange(N)
        if (x >> w) & 1:
            opts.append(w)
            if len(opts) >= 110:
                break
    if not opts:
        lsb = x & -x
        opts = [lsb.bit_length() - 1]

    w = max(opts, key=lambda z: (deg[z], random.random() * 70))
    return (v, w)


def find_clique_bt(adj, deg, start_vertices, node_limit=1600, branch=65):
    C = list(start_vertices)
    common = allmask
    used_groups = {v // SIZE for v in C}
    for v in C:
        common &= adj[v]
    for g in used_groups:
        common &= ~group_masks[g]

    nodes = [0]

    def rec(C, common):
        nodes[0] += 1
        if nodes[0] > node_limit:
            return None
        need = K - len(C)
        if need == 0:
            return tuple(sorted(C))
        if common.bit_count() < need:
            return None

        opts = []
        x = common
        while x and len(opts) < branch * 7:
            lsb = x & -x
            opts.append(lsb.bit_length() - 1)
            x -= lsb

        opts.sort(key=lambda v: (-deg[v], random.random()))
        for v in opts[:branch]:
            new_common = common & adj[v] & ~group_masks[v // SIZE]
            res = rec(C + [v], new_common)
            if res is not None:
                return res
        return None

    return rec(C, common)


def find_next(adj, deg, trials=55):
    best = None
    best_score = -10 ** 18
    for _ in range(trials):
        e = random_edge_high(adj, deg)
        if e is None:
            return None
        C = find_clique_bt(adj, deg, e, node_limit=1580, branch=62)
        if C is None:
            continue
        degrees = [deg[v] for v in C]
        score = sum(degrees) - 6 * max(degrees) - min(degrees)
        if score > best_score:
            best_score = score
            best = C
    return best


def find_next_loose(adj, deg, trials=35):
    best = None
    best_score = -10 ** 18
    for _ in range(trials):
        e = random_edge_high(adj, deg)
        if e is None:
            return None
        C = find_clique_bt(adj, deg, e, node_limit=1900, branch=58)
        if C is None:
            continue
        degrees = [deg[v] for v in C]
        score = sum(degrees) - 4 * max(degrees)
        if score > best_score:
            best_score = score
            best = C
    return best


def repair_attempt(sol, remove_num, fill_seconds):
    sol2 = list(sol)
    if len(sol2) < 50:
        return sol2

    num_to_remove = min(remove_num, len(sol2) // 2 + 30)
    idxs = sorted(random.sample(range(len(sol2)), num_to_remove), reverse=True)
    for idx in idxs:
        sol2.pop(idx)

    adj, deg = init_cross_adj()
    for C in sol2:
        remove_clique(adj, deg, C)

    start = time.time()
    while time.time() - start < fill_seconds:
        C = find_next(adj, deg, trials=45)
        if C is None:
            break
        remove_clique(adj, deg, C)
        sol2.append(C)
    return sol2


def verify_cross_solution(sol):
    seen = set()
    for C in sol:
        if len(C) != 11 or len(set(C)) != 11:
            return False
        for i, v in enumerate(C):
            for w in C[i + 1:]:
                if v // SIZE == w // SIZE:
                    return False
                e = (min(v, w), max(v, w))
                if e in seen:
                    return False
                seen.add(e)
    return True


def main():
    print("=== WERSJA v3 ===")
    random.seed(54321)

    sol = []
    adj, deg = init_cross_adj()
    start_time = time.time()

    # ==================== ETAP 1: GREEDY ====================
    print("Etap 1: Ulepszone Greedy...")
    last_improvement = time.time()

    while time.time() - start_time < 320:
        C = find_next(adj, deg, trials=55)

        if C is None:
            print("  Brak kliki → włączam tryb luźny...")
            C = find_next_loose(adj, deg, trials=35)

        if C is None:
            if time.time() - last_improvement > 40:
                print("  Brak postępu → kończę Greedy")
                break
            continue

        remove_clique(adj, deg, C)
        sol.append(C)
        last_improvement = time.time()

        if len(sol) % 50 == 0:
            print(f"  Znaleziono {len(sol)} klik krzyżowych...")

    print(f"Greedy zakończone → {len(sol)} klik krzyżowych\n")

    # ==================== ETAP 2: LOCAL SEARCH ====================
    print("Etap 2: Agresywny Local Search (może trwać 40-90 minut)...")
    best_sol = list(sol)
    current_sol = list(sol)
    temperature = 130.0
    it = 0
    last_save = time.time()

    while time.time() - start_time < 7200:
        it += 1
        r = random.choice([120, 170, 220, 280, 350])
        fill_sec = 12.0 if temperature > 35 else 16.0

        candidate = repair_attempt(current_sol, r, fill_sec)

        delta = len(candidate) - len(current_sol)
        if delta > 0 or random.random() < (2.71828 ** (delta * 1.15 / temperature)):
            current_sol = candidate
            if len(current_sol) > len(best_sol):
                best_sol = list(current_sol)
                total = len(best_sol) + INSIDE_BLOCKS
                print(f"  → NOWY REKORD! {len(best_sol)} klik krzyżowych | Razem bloków: {total} | Temp: {temperature:.1f}")

        temperature *= 0.989

        if it % 8 == 0:
            total_b = len(best_sol) + INSIDE_BLOCKS
            print(f"  [Status] Iter {it} | Najlepszy: {len(best_sol)} + 51 = {total_b} | Temp: {temperature:.1f}")

        if time.time() - last_save > 300: 
            with open("najlepsze_rozwiazanie.txt", "w") as f:
                for clique in best_sol:
                    f.write(" ".join(map(str, sorted(clique))) + "\n")
            last_save = time.time()

    # ==================== WYNIK KOŃCOWY ====================
    total_blocks = len(best_sol) + INSIDE_BLOCKS
    covered = total_blocks * 55
    elapsed = (time.time() - start_time) / 60

    print("\n" + "=" * 90)
    print("WYNIK KOŃCOWY")
    print("=" * 90)
    print(f"Liczba klik krzyżowych : {len(best_sol)}")
    print(f"Łączna liczba bloków   : {total_blocks}")
    print(f"Pokryte krawędzie      : {covered}")
    print(f"Procent pokrycia       : {covered / TOTAL_EDGES * 100:.2f}%")
    print(f"Czas całkowity         : {elapsed:.1f} minut")
    print("Weryfikacja poprawności:", "Poprawna" if verify_cross_solution(best_sol) else "Błąd")
    print("=" * 90)

    with open("najlepsze_rozwiazanie.txt", "w") as f:
        for clique in best_sol:
            f.write(" ".join(map(str, sorted(clique))) + "\n")

    print("\nRozwiązanie zapisano do pliku: najlepsze_rozwiazanie.txt")
    input("\nNaciśnij Enter, aby zakończyć...")


if __name__ == "__main__":
    main()
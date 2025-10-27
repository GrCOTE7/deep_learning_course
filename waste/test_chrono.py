from libs.chrono import chrono

print("🎯 CHRONO SIMPLIFIÉ (Compte 1 000 000)")
print("=" * 30)

chrono.start()
for i in range(1_000_000):
    x = i * 2
chrono.elapsed()

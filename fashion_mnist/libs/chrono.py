import time


class chrono:
    _start_time = None

    @classmethod
    def start(cls):
        cls._start_time = time.time()
        print("⏱️  Chrono démarré...")

    @classmethod
    def elapsed(cls):
        if cls._start_time is None:
            print("❌ Appelez d'abord chrono.start()")
            return None

        elapsed_time = time.time() - cls._start_time
        formatted = cls.format_time(elapsed_time)
        print(f"⏱️  Temps: {formatted}")
        return elapsed_time

    @staticmethod
    def format_time(elapsed_seconds):
        """Formate un temps en secondes au format HH:MM:SS.ms"""
        hours = int(elapsed_seconds // 3600)
        minutes = int((elapsed_seconds % 3600) // 60)
        seconds = elapsed_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"


if __name__ == "__main__":
    print("🎯 CHRONO SIMPLIFIÉ (Compte jusqu'à1 000 000)")

    print("=" * 55)
    chrono.start()
    for i in range(1_000_000):
        x = i * 2
    chrono.elapsed()

    print("=" * 55)
    chrono.start()
    time.sleep(1.77)
    chrono.elapsed()

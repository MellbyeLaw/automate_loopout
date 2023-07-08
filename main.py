import sys
from bos import BOS

def main():
    umbrel_2fa, umbrel_password, bos_username, bos_password,\
         amount, n_times, best_ppm, worst_ppm = sys.argv[1:]
    amount = abs(int(amount))
    n_times = abs(int(n_times))
    best_ppm = abs(int(best_ppm))
    worst_ppm = abs(int(worst_ppm))

    b = BOS(
        umbrel_2fa=umbrel_2fa,
        umbrel_password=umbrel_password,
        bos_username=bos_username,
        bos_password=bos_password,
        max_ppm=worst_ppm
    )
    b.loop_out(amount=amount, n_times=n_times, max_ppm=best_ppm)

if __name__ == '__main__':
    main()
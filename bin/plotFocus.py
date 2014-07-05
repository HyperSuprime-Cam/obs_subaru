#!/usr/bin/env python
import os, re
import sqlite3
import argparse
import numpy
from matplotlib import pyplot

def main():
    parser = argparse.ArgumentParser(description="""Plot focus position from the observing log sqlite file

N.b. You can obtain the sqlite file from the "sqlite3" link at the bottom of
    http://hsca-web01.subaru.nao.ac.jp/michitaro/web-preview
""")
    parser.add_argument('db', help="Sqlite3 data file")
    parser.add_argument('--rerun', required=True, help="Rerun to plot")
    parser.add_argument('--error', action="store_true",
                        help="Plot the focus error not the focus position", default=False)
    parser.add_argument('--noFwhm', action="store_true",
                        help="Don't include the FWHM panel", default=False)
    parser.add_argument('--correctFwhmForFocusError', action="store_true",
                        help="Correct measured FWHM for focus error", default=False)
    parser.add_argument('--out', '-o', help="Output file")
    parser.add_argument('--dpi', type=int, help="Dots per inch for output file")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''
        SELECT visit, fwhm, focus, focus_error, header_json FROM frames WHERE rerun = ? AND focus IS NOT NULL
        ''',
        (args.rerun, )
    )

    visit, fwhm, focus, focus_error, header = numpy.array(list(list(line) for line in c)).T
    visit = visit.astype(int)
    fwhm = 0.168*fwhm.astype(float)     # convert from pixels to arcsec
    focus = focus.astype(float)
    focus_error = focus_error.astype(float)

    import json
    foc_val = numpy.empty_like(focus)
    focusSweepVisits = []
    for i, cards in enumerate(header):
        cards = json.loads(cards)
        foc_val[i] = cards["FOC-VAL"]

        if re.search(r"^focus", cards["OBJECT"], re.IGNORECASE):
            focusSweepVisits.append(visit[i])
            fwhm[i] = numpy.nan
            focus[i] = numpy.nan
            foc_val[i] = numpy.nan


    axes = []
    if args.noFwhm:
        ax0 = pyplot.subplot2grid((1, 1), (0, 0))
    else:
        ax0 = pyplot.subplot2grid((3, 1), (1, 0), rowspan=2)
    axes.append(ax0)

    if args.error:
        ax0.errorbar(visit, -focus, yerr=focus_error, fmt='+', ms=2, label="Focus error")
        ax0.axhline(0.0, color='gray')
    else:
        ax0.errorbar(visit, foc_val, label="foc-val")
        ax0.errorbar(visit, foc_val - focus, yerr=focus_error, fmt='+', ms=2, label="predicted")

    ax0.legend(loc='best')
    ax0.set_ylabel("Focus %s (mm)" % ("error" if args.error else "position"))

    if not args.noFwhm:
        ax1 = pyplot.subplot2grid((3, 1), (0, 0), sharex=ax0)
        axes.append(ax1)

        ax1.plot(visit, fwhm, '.', label="measured")
        if args.correctFwhmForFocusError:
            # rms^2 = rms_*^2 + alpha*focus^2  where rms is in arcsec and focus in mm
            alpha = 4.2e-2              # rms and focus in mm from zemacs;  ../hsc/zemax_config?_0.0.dat
            alpha /= 1.6                # alpha assumes that we're using a Gaussian-weighted rms
            alpha *= (0.168/0.015)**2   # convert to arcsec^2
            alpha *= 8*numpy.log(2)     # convert rms^2 to fwhm^2 for a Gaussian

            
            ax1.plot(visit, numpy.sqrt(fwhm**2 - alpha*focus**2), '.', label="corrected")
            ax1.legend(loc='best')
        ax1.set_ylabel("FWHM (arcsec)")

    x0, x1 = min(visit), max(visit)
    for ax in axes:
        for v in focusSweepVisits:
            ax.axvline(v, color='red')

        ax.set_xticks(range(10*int(0.1*x0), int(10*int(0.1*x1)), 5), minor=True)
        ax.set_xlim(x0 - 0.05*(x1 - x0), x1 + 0.05*(x1 - x0)) 
        ax.grid()

    ax0.set_xlabel("visit")

    pyplot.title("Rerun %s" % args.rerun)
    
    if args.out:
        pyplot.savefig(args.out, dpi=args.dpi)
    else:
        pyplot.interactive(True)
        pyplot.show()
        raw_input("Hit any key to exit ")

if __name__ == '__main__':
    main()

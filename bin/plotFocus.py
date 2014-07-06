#!/usr/bin/env python
import os, re
import sqlite3
import argparse
import numpy;  np = numpy
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
    parser.add_argument('--showAltitude', action="store_true",
                        help="Plot the altitude", default=False)
    parser.add_argument('--noFwhm', action="store_false", dest="showFwhm",
                        help="Don't include the FWHM panel", default=True)
    parser.add_argument('--correctFwhmForFocusError', action="store_true",
                        help="Correct measured FWHM for focus error", default=False)
    parser.add_argument('--estimateFocus', action="store_true",
                        help="Estimate the focus using a Kalman filter", default=False)
    parser.add_argument('--modelErrorAsAcceleration', action="store_true",
                        help="Model state error as a stochastic acceleration", default=False)
    parser.add_argument('--jitter', type=float,
                        help="Std. dev. of stochastic jitter in focus", default=None)
    
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
    altitude = numpy.empty_like(focus)
    mjd = numpy.empty_like(focus)
    focusSweepVisits = []
    for i, cards in enumerate(header):
        cards = json.loads(cards)
        foc_val[i] = cards["FOC-VAL"]
        altitude[i] = cards["ALTITUDE"]
        mjd[i] = cards["MJD"]

        if re.search(r"^focus", cards["OBJECT"], re.IGNORECASE):
            focusSweepVisits.append(visit[i])
            fwhm[i] = numpy.nan
            focus[i] = numpy.nan
            foc_val[i] = numpy.nan

    mjd -= int(mjd[0])
    mjd *= 24*60                        # minutes
    #
    # Estimate the focus position?
    #
    if args.estimateFocus:
        #
        # Handle each section at constant altitude and without long gaps separately
        #
        sections = []                   # good sections
        dAltitude = 5
        dMjd = 20                   # minutes
        i0 = -1
        for i in range(len(altitude)):
            if False and not np.isfinite(focus[i]):
                if i0 > 0 and i > i0:
                    sections.append((i0, i))
                    i0 = -1

                continue

            if i0 < 0:
                i0 = i

            if i > 0 and (abs(altitude[i] - altitude[i-1]) > dAltitude or
                          abs(mjd[i] - mjd[i-1]) > dMjd):
                if i0 > 0 and i > i0:
                    sections.append((i0, i))
                i0 = i
                    
        sections.append((i0, len(focus)))
        
        t = mjd.astype(float)                 # observation time

        jitter = args.jitter
        if args.modelErrorAsAcceleration:
            errorModel = "acceleration"
            if jitter is None:
                jitter = 2e-5                          # per-point s.d. due to inadequacy of model
            jitter *= 2/np.median(np.gradient(mjd))**2 # convert to s.d. of an acceleration
        else:
            errorModel = None
            if jitter is None:
                jitter = 2e-3

        focusHat = np.nan + focus
        focusHat_error = np.nan + focus_error
        for i0, i1 in sections:
            section = range(i0, i1)

            z, z_error = (foc_val - focus)[section], focus_error[section]
            focusHat[section], focusHat_error[section] = kalman(t[section], z, z_error, jitter,
                                                                errorModel=errorModel, visit=visit[section])
    #
    # Time to plot
    #
    axes = []
    if not args.showFwhm and not args.showAltitude:
        ax0 = pyplot.subplot2grid((1, 1), (0, 0))
    else:
        ax0 = pyplot.subplot2grid((3, 1), (1, 0), rowspan=2)
    axes.append(ax0)

    title = "Rerun %s" % args.rerun

    if args.error:
        ax0.errorbar(visit, -focus, yerr=focus_error, fmt='+', ms=2, label="Focus error")
        ax0.axhline(0.0, color='gray')
    else:
        ax0.errorbar(visit, foc_val, label="foc-val")
        ax0.errorbar(visit, foc_val - focus, yerr=focus_error, fmt='+', ms=4, label="predicted")

    if args.estimateFocus:
        if args.error:
            focusHat -= foc_val

        for i, s in enumerate(sections):
            s = range(*s)
            if False:
                ax0.errorbar(visit[s], focusHat[s], yerr=focusHat_error[s], ms=2, color='red',
                             label="Kalman" if i == 0 else None)
            else:

                if i == 0:
                    ax0.plot([np.nan], color='red', label="Kalman")
                    
                n = len(s)
                xvec = np.empty(2*n);  yvec = np.empty_like(xvec)
                xvec[0:n] = visit[s];  xvec[n:] = visit[s][::-1]

                yvec[0:n] = (focusHat + focusHat_error)[s]
                yvec[n:] =  (focusHat - focusHat_error)[s][::-1]

                p = pyplot.Polygon(zip(xvec, yvec), color='red', alpha=0.5)
                ax0.add_artist(p)

        tmp = focusHat[np.isfinite(focusHat)]
        if len(tmp):
            title += "  Best Focus: %.2fmm" % tmp[-1]

    ax0.legend(loc='best').draggable()
    ax0.set_ylabel("Focus %s (mm)" % ("error" if args.error else "position"))

    if args.showAltitude or args.showFwhm:
        ax1 = pyplot.subplot2grid((3, 1), (0, 0), sharex=ax0)
        axes.append(ax1)

    if args.showAltitude:
        ax1.plot(visit, altitude, '.', label="alt")
        ax1.set_ylabel("Altitude")
    elif args.showFwhm:
        ax1.plot(visit, fwhm, '.', label="measured")
        if args.correctFwhmForFocusError:
            # rms^2 = rms_*^2 + alpha*focus^2  where rms is in arcsec and focus in mm
            alpha = 4.2e-2              # rms and focus in mm from zemacs;  ../hsc/zemax_config?_0.0.dat
            alpha /= 1.6                # alpha assumes that we're using a Gaussian-weighted rms
            alpha *= (0.168/0.015)**2   # convert to arcsec^2
            alpha *= 8*numpy.log(2)     # convert rms^2 to fwhm^2 for a Gaussian

            
            ax1.plot(visit, numpy.sqrt(fwhm**2 - alpha*focus**2), '.', label="corrected")
            ax1.legend(loc='best').draggable()
        ax1.set_ylabel("FWHM (arcsec)")

    x0, x1 = min(visit), max(visit)
    for ax in axes:
        for v in focusSweepVisits:
            ax.axvline(v, color='cyan')

        ax.set_xticks(range(10*int(0.1*x0), int(10*int(0.1*x1)), 5), minor=True)
        ax.set_xlim(x0 - 0.05*(x1 - x0), x1 + 0.05*(x1 - x0)) 
        ax.grid()

    ax0.set_xlabel("visit")

    pyplot.title(title)
    
    if args.out:
        pyplot.savefig(args.out, dpi=args.dpi)
    else:
        pyplot.interactive(True)
        pyplot.show()
        raw_input("Hit any key to exit ")

def kalman(t, z, dz, jitter, errorModel, visit=None):
    """Estimate the current focus using a Kalman filter
    \param t  Time of measurement
    \param z  Measured focus
    \param dz Error in z
    \param jitter S.d. of intrinsic focus noise
    \param errorModel How to model the intrinsic noise
    \param visit  Visits corresponding to t, z, and dz (debugging only)

The tricky part is choosing the noise model for the focus.  Two options are supported:
if errorModel == "acceleration":
    Assume that the focus has a linear trend with an extra stochastic acceleration:
           focus + d focus/dt DeltaT + 1/2 N(0, jitter^2) DeltaT^2
else
    Assume that d focus/dt has a stochasitc term added:
           focus + (d focus/dt + N(0, (jitter/DeltaT)^2)) DeltaT
    """
    #
    # Find the first good value
    #
    for i0 in range(len(t)):
        if np.isfinite(z[i0]):
            break
    #
    # Kalman filter
    #
    F = np.ones((2, 2))                 # transition matrix
    F[1, 0] = 0;  F[0, 1] = np.nan

    H = np.array([1, 0])                # observation model projecting true state onto observations
    P = np.zeros((2, 2))                # covariance of the true state
    #
    # Initial guesses
    #
    large = 1e6
    x = np.array([z[i0], 0])             # values are unimportant as P >> 0
    P[0, 0] = P[1, 1] = large           # unknown large covariances as we don't know the initial state

    zhat  = np.nan + np.zeros_like(t)
    dzhat = np.nan + np.zeros_like(t)
    
    told = t[i0]
    zhat[i0] = z[i0]
    dzhat[i0] = dz[i0]
    for i in range(i0 + 1, len(t)):
        dt = t[i] - told
        R = dz[i]**2                    # covariance of observation

        F[0, 1] = dt

        if errorModel == "acceleration": # model errors in model as an acceleration term
            G = np.array([dt**2/2, dt]) # change in state if stochastic acceleration jitter == 1
            Q = np.outer(G, G.T)
        elif True:                      # model error in model as a jitter in dfocus/dtime
            Q = np.array([[0, 0], [0, 1/dt]], dtype=float)

        Q *= jitter**2                  # covariance of stochastic term in model

        # Predict
        x = F.dot(x)                    # estimate true state
        P = F.dot(P).dot(F.T) + Q       # and its covariance

        if not np.isfinite(z[i]):
            zhat[i] = x[0]
            dzhat[i] = np.sqrt(P[0, 0])

            continue

        # Update
        y = z[i] - H.dot(x)             # residual of observation
        S = H.dot(P).dot(H.T) + R       # y's covariance
        K = P.dot(H.T)/S                # Kalman gain

        x = x + K.dot(y)                # updated state estimate
        P = (np.identity(1) - K.dot(H))*P # updated state covariance

        if i == 1:
            P[1, 1] = large             # we have no idea what the initial velocity was

        zhat[i] = x[0]
        dzhat[i] = np.sqrt(P[0, 0])

    return zhat, dzhat

if __name__ == '__main__':
    main()

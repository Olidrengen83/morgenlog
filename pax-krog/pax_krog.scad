// Krog til at hænge over en PAX/Komplement-skuffefront (17 mm).
// Samme mål som lav_krog.py. Print liggende på siden (bredden = Z på printeren).

front      = 17;    // skuffefrontens tykkelse
sloer      = 0.4;   // luft i slidsen -> 17.4 mm indvendigt
vaeg       = 3.2;   // godstykkelse i klemmen
ben_ude    = 32;    // ben ned ad forsiden
ben_inde   = 18;    // ben ned inde i skuffen
arm_t      = 4;     // krogarmens tykkelse
raek       = 30;    // hvor langt krogen rager ud
stig       = 5;     // armen hælder opad udad
spids_h    = 16;    // spidsens højde
spids_laen = 2;     // spidsen læner ind mod fronten
gusset     = 12;    // forstærkning i hjørnet
bredde     = 25;    // krogens bredde langs fronten
rund       = 1;     // afrunding af udvendige hjørner
$fn = 48;

slids = front + sloer;

module klemme() {
    offset(r = rund) offset(delta = -rund) union() {
        translate([-vaeg, 0])        square([slids + 2 * vaeg, vaeg]);
        translate([-vaeg, -ben_ude]) square([vaeg, ben_ude + vaeg]);
        translate([slids, -ben_inde]) square([vaeg, ben_inde + vaeg]);
    }
}

module profil() {
    y0 = -ben_ude + arm_t / 2;
    p0 = [-vaeg + 0.5, y0];
    p1 = [-vaeg - raek, y0 + stig];
    p2 = [p1[0] + spids_laen, p1[1] + spids_h];
    union() {
        klemme();
        hull() { translate(p0) circle(d = arm_t); translate(p1) circle(d = arm_t); }
        hull() { translate(p1) circle(d = arm_t); translate(p2) circle(d = arm_t); }
        polygon([[-vaeg, -ben_ude + gusset], [-vaeg, -ben_ude],
                 [-vaeg - gusset, -ben_ude + gusset * stig / raek + 1]]);
    }
}

// Liggende på siden, klar til print:
linear_extrude(height = bredde) profil();

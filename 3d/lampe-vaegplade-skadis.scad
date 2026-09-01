// ============================================================
// Vægplade til lampe med nøglehuls-ophæng ("omvendt lollipop")
// Monteres på IKEA SKÅDIS pegboard med indbyggede kroge på bagsiden.
//
// Forsiden har 2 "skruehoveder" (paddehatte-tappe) med 78 mm
// center-center, som lampens nøglehulsudskæringer hænges på.
//
// Alle mål i mm. Justér parametrene herunder efter din lampe:
//  - peg_shaft_d skal være mindre end den smalle del af nøglehullet
//  - peg_head_d skal være mindre end det store hul, men større end slidsen
//  - peg_shaft_l skal være lidt større end tykkelsen på lampens plade
//
// Print: Stil pladen lodret på underkanten (som den hænger).
// Slå supports til – der skal kun support under krogenes nedadvendte
// læber. Brim anbefales.
// ============================================================

// ---------- Plade ----------
plate_w = 100;    // bredde
plate_h = 60;     // højde
plate_t = 6;      // tykkelse

// ---------- "Skruehoveder" (nøglehulstappe) ----------
peg_cc      = 78;   // center-center afstand
peg_shaft_d = 4.2;  // halsens diameter (skal passe i nøglehullets slids)
peg_shaft_l = 4.0;  // frit stykke bag hovedet (plads til lampens plade)
peg_head_d  = 8.0;  // hovedets diameter (skal passe i nøglehullets store hul)
peg_head_t  = 2.5;  // hovedets tykkelse

// ---------- SKÅDIS-kroge (bagside) ----------
// SKÅDIS: huller 5 x 15 mm i 40 mm grid, pladetykkelse ca. 5,1 mm
skadis_pitch   = 40;    // hulafstand
skadis_board_t = 5.2;   // pegboardets tykkelse
hook_w         = 4.6;   // krogbredde (hullet er 5 mm)
hook_h         = 4.6;   // armens højde
hook_clear     = 0.4;   // luft bag boardet
hook_lip_l     = 8;     // læbens længde nedad bag boardet
hook_lip_t     = 3;     // læbens tykkelse
gusset         = 3;     // 45-graders støttekile under armen

$fn = 64;

hook_reach = skadis_board_t + hook_clear + hook_lip_t; // arm-længde bag pladen

module peg() {
    // hals + 45-graders overgang + fladt hoved (som et skruehoved)
    cylinder(d = peg_shaft_d, h = peg_shaft_l);
    translate([0, 0, peg_shaft_l])
        cylinder(d1 = peg_shaft_d, d2 = peg_head_d,
                 h = (peg_head_d - peg_shaft_d) / 2);
    translate([0, 0, peg_shaft_l + (peg_head_d - peg_shaft_d) / 2])
        cylinder(d = peg_head_d, h = peg_head_t);
}

module skadis_hook() {
    // Arm gennem hullet, læbe nedad bag boardet, kile under armen.
    // Origo = hulcenter på pladens bagside (z=0 er bagsiden, -z bagud).
    translate([-hook_w/2, -hook_h/2, -hook_reach])
        cube([hook_w, hook_h, hook_reach]);                 // arm
    translate([-hook_w/2, -hook_h/2 - hook_lip_l, -hook_reach])
        cube([hook_w, hook_lip_l, hook_lip_t]);             // læbe
    translate([-hook_w/2, 0, 0])
        rotate([0, 90, 0])                                   // kile (45 gr.)
            linear_extrude(height = hook_w)
                polygon([[0, -hook_h/2],
                         [gusset, -hook_h/2],
                         [0, -hook_h/2 - gusset]]);
}

// ---------- Samlet model ----------
// z=0 er pladens bagside, forsiden vender mod +z.
union() {
    translate([-plate_w/2, -plate_h/2, 0])
        cube([plate_w, plate_h, plate_t]);

    // Tappe på forsiden, 78 mm cc, lodret centreret
    for (x = [-peg_cc/2, peg_cc/2])
        translate([x, 0, plate_t])
            peg();

    // 4 SKÅDIS-kroge i 40 mm grid på bagsiden
    for (x = [-skadis_pitch/2, skadis_pitch/2],
         y = [-skadis_pitch/2, skadis_pitch/2])
        translate([x, y, 0])
            skadis_hook();
}

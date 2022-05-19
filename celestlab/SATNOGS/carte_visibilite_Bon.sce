/////////////////////////// Variable ////////////////

rTerre = 6378e3 ;
t0 = 21915;    // initial time
time_step =2/86400;   // in days
duration =2/24; // in days
t = t0 //+ (0:time_step:duration) ;  // list of computation dates
pas_lat = 4;
pas_lon = 4;


alt = 500000;

//====================================  generer la constellation et son mouvement  ======================================

[kepConst, sat_angle_lim, cen_angle_lim, freq_emission_const, freq_reception_const] = generate_constellation("IridiumNext");

const = [] ;

for kep0=kepConst //calcul pour chaque satellite leur paramètre polaire pdt la liste t ( de 0 à tfinal par t_pas)
    kep = CL_ex_secularJ2(t0, kep0, t);
    [pos, vel] = CL_oe_kep2car(kep);
   
    pos_con = pos;
    const = [const, pos_con];
end

//==================================== visibilité ====================================
data = [] ;
for lon=-180:pas_lon:180
    ligne = [];
    for lat=-90:pas_lat:90
        [pos_sat, jacob] = CL_co_sph2car([lon*%pi/180; lat*%pi/180; (rTerre+alt)]);
        visibles = 0;
        sat_angle = CL_vectAngle(CL_dMult(ones(1,75),pos_sat)-const, -const);
            cen_angle = CL_vectAngle(pos_sat, const);
        for k=1:75
            //eclipse = CL_gm_eclipseCheck(pos_sat, pos_con, sr1=10);
            visibles = ((sat_angle(k) < sat_angle_lim) & (cen_angle(k) < cen_angle_lim))*1 + visibles;
        end
        ligne = [ligne, visibles];
        printf(".")
    end
    data = [data; ligne] ;
    printf("%d"+ascii(10), lon)
end


//=====================================   trace la visibilite   =================================
Lon=[-180: pas_lon:180];
Lat=[-90 : pas_lat: 90] ;


// ==========  plot heatmap
scf(0)
f=gcf();
color_map = hotcolormap(max(data)*2)
grayplot(Lon,Lat,data)
//Matplot(data,"011",rect = [0, -90, 360, 90])
f.color_map = color_map;
colorbar(min(data),max(data))
CL_plot_earthMap(color_id=max(data)*2)
CL_plot_ephem(pos_sat,color_id=max(data)*2);
title('Carte de visibilite à 500 km d altitude par rapport à la constellation iridium Next')
xlabel('longitude (par pas de 2)(deg)')
ylabel('lat (par pas de 1)(deg)')
CL_g_stdaxes();


// =========  plot 3D polar map


scf(1)
R = rTerre + alt;
[A,Th] = meshgrid(Lon,Lat);
Z = R*sind(Th);
X = R*cosd(Th).*cosd(A);
Y = R*cosd(Th).*sind(A);
Ncolors = 100;                  // Number of coding colors
//temp = pmodulo(A+Th,Ncolors)+1; // Here gives the spherical mapping of your data
values =(data');
g = gcf();
g.color_map = hotcolormap(max(data)*2);
colorbar(min(data),max(data))
surf(X,Y,Z,values)
ax = gca();
ax.isoview = 'on';
e = gce();
e.thickness = 0;
e.thickness = 0; // hides the mesh
e.color_flag = 3; // switches to interpolated colors
title('Carte de visibilite à 500 km d altitude par rapport à la constellation iridium Next')
CL_g_stdaxes();


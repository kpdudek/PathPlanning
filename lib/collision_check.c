#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>

double cross_product(double v1 [2][1], double v2 [2][1]){
    return v1[0][0] * v2[1][0] - v2[0][0] * v1[1][0];
}

double direction(double v1 [2][1], double v2 [2][1], double v3 [2][1]){
    double v3_v1 [2][1] = {{v3[0][0]-v1[0][0]},{v3[1][0]-v1[1][0]}};
    double v2_v1 [2][1] = {{v2[0][0]-v1[0][0]},{v2[1][0]-v1[1][0]}};
    double cross = cross_product(v3_v1, v2_v1);
    return cross;
}

int edge_is_collision(double e1 [2][2], double e2 [2][2]){
    double v1 [2][1] = {{e1[0][0]},{e1[1][0]}};
    double v2 [2][1] = {{e1[0][1]},{e1[1][1]}};
    double v3 [2][1] = {{e2[0][0]},{e2[1][0]}};
    double v4 [2][1] = {{e2[0][1]},{e2[1][1]}};

    double d1 = direction(v3, v4, v1);
    double d2 = direction(v3, v4, v2);
    double d3 = direction(v1, v2, v3);
    double d4 = direction(v1, v2, v4);

    if(((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) && ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))){
        return 1;
    }
    else{
        return 0;
    }
}

int sphere_is_collision(double s1_pose [], double s1_rad, double s2_pose [], double s2_rad){
    /*
    This function determines if two spheres are in collision
    positive r --> solid sphere
    negative r --> hollow sphere
    */
    int collision = 0;
    double dist = pow(pow(s1_pose[0]+s2_pose[0],2)+pow(s1_pose[1]+s2_pose[1],2),0.5);

    if(s1_rad < 0 && s2_rad < 0){
        return 1;
    }
    else if(s1_rad < 0 || s2_rad < 0){
        if(dist > -1*(s1_rad + s2_rad)){
            return 1;
        }
        else{
            return 0;
        }
    }
    else{
        if(dist < (s1_rad + s2_rad)){
            return 1;
        }
        else{
            return 0;
        }
    }

    return collision;
}

int polygon_is_collision(double poly1 [], int poly1_row, int poly1_col, double poly2 [], int poly2_row, int poly2_col){
    int collision = 0;
    double e1 [2][2] = {};
    double e2 [2][2] = {};

    int count = 0;
    for(int i = 0; i < poly1_col; i++){
        for(int j = 0; j < poly2_col; j++){
            if(i == poly1_col-1){
                e1[0][0] = poly1[i];
                e1[1][0] = poly1[i+poly1_col];
                e1[0][1] = poly1[0];
                e1[1][1] = poly1[0+poly1_col];
            }
            else{
                e1[0][0] = poly1[i];
                e1[1][0] = poly1[i+poly1_col];
                e1[0][1] = poly1[i+1];
                e1[1][1] = poly1[i+1+poly1_col];
            }

            if(j == poly2_col-1){
                e2[0][0] = poly2[j];
                e2[1][0] = poly2[j+poly2_col];
                e2[0][1] = poly2[0];
                e2[1][1] = poly2[0+poly2_col];
            }
            else{
                e2[0][0] = poly2[j];
                e2[1][0] = poly2[j+poly2_col];
                e2[0][1] = poly2[j+1];
                e2[1][1] = poly2[j+1+poly2_col];
            }

            if(edge_is_collision(e1,e2)==1){
                collision = 1;
                break;
            }
            count++;
        }
        if(collision == 1){
            break;
        }
    }
    return collision;
}

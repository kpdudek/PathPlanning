#include <iostream>
#include <math.h>
#include <chrono>

#define PI 3.14159265
 
using namespace std;

class Polygon {
    public:
        Polygon(int num, double offset); 
        int num_vert;
        double vertices [2][50] = {};
        double offset;
    private:
        void Set_Vertices(void);
}; 

// Member functions definitions including constructor
Polygon::Polygon(int num, double off) {
    cout << "Polygon is being created..." << endl;
    num_vert = num;
    offset = off;

    this->Set_Vertices();
}

void Polygon::Set_Vertices(void) {
    cout << "Setting vertices..." << endl;
    double delt = 2.*PI / this->num_vert;
    double ang = 0.0;

    for(int i = 0; i < this->num_vert; i++){
        this->vertices[0][i] = cos(ang) + this->offset;
        this->vertices[1][i] = sin(ang) + this->offset;
        ang = ang + delt;
    }
}

double cross_product(double v1 [2][1], double v2 [2][1]){
    return v1[0][0] * v2[1][0] - v2[0][0] * v1[1][0];
}

double direction(double v1 [2][1], double v2 [2][1], double v3 [2][1]){
    double v3_v1 [2][1] = {{v3[0][0]-v1[0][0]},{v3[1][0]-v1[1][0]}};
    double v2_v1 [2][1] = {{v2[0][0]-v1[0][0]},{v2[1][0]-v1[1][0]}};
    double cross = cross_product(v3_v1, v2_v1);
    return cross;
}

bool edge_is_collision(double e1 [2][2], double e2 [2][2]){
    double v1 [2][1] = {{e1[0][0]},{e1[1][0]}};
    double v2 [2][1] = {{e1[0][1]},{e1[1][1]}};
    double v3 [2][1] = {{e2[0][0]},{e2[1][0]}};
    double v4 [2][1] = {{e2[0][1]},{e2[1][1]}};

    double d1 = direction(v3, v4, v1);
    double d2 = direction(v3, v4, v2);
    double d3 = direction(v1, v2, v3);
    double d4 = direction(v1, v2, v4);

    if(((d1 > 0 and d2 < 0) || (d1 < 0 and d2 > 0)) && ((d3 > 0 and d4 < 0) || (d3 < 0 and d4 > 0))){
        return true;
    }
    else{
        return false;
    }
}

bool polygon_is_collision(Polygon poly1, Polygon poly2){
    bool collision = false;
    double e1 [2][2] = {};
    double e2 [2][2] = {};

    for(int i = 0; i < poly1.num_vert; i++){
        for(int j = 0; i < poly2.num_vert; j++){
            if(i == poly1.num_vert-1){
                e1[0][0] = poly1.vertices[0][i];
                e1[1][0] = poly1.vertices[1][i];
                e1[0][1] = poly1.vertices[0][0];
                e1[1][1] = poly1.vertices[1][0];
            }
            else{
                e1[0][0] = poly1.vertices[0][i];
                e1[1][0] = poly1.vertices[1][i];
                e1[0][1] = poly1.vertices[0][i+1];
                e1[1][1] = poly1.vertices[1][i+1];
            }

            if(j == poly2.num_vert-1){
                e2[0][0] = poly2.vertices[0][j];
                e2[1][0] = poly2.vertices[1][j];
                e2[0][1] = poly2.vertices[0][0];
                e2[1][1] = poly2.vertices[1][0];
            }
            else{
                e2[0][0] = poly2.vertices[0][j];
                e2[1][0] = poly2.vertices[1][j];
                e2[0][1] = poly2.vertices[0][j+1];
                e2[1][1] = poly2.vertices[1][j+1];
            }

            if(edge_is_collision(e1,e2)==true){
                collision = true;
                break;
            }
        }
        if(collision == true){
            break;
        }
    }
    return collision;
}

// Main function for the program
int main() {
    Polygon poly1(40.,0.0);
    cout << "Number of vertices 1: " << poly1.num_vert << endl;

    Polygon poly2(40.,0.2);
    cout << "Number of vertices 2: " << poly2.num_vert << endl;
    
    bool col_res;
    auto start = std::chrono::high_resolution_clock::now();    
    col_res = polygon_is_collision(poly1,poly2);
    auto end = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> elapsed_seconds = end-start;
    printf("Collision result: %d\n",col_res);
    printf("Collision check took: %f\n",elapsed_seconds.count());

    return 0;
}
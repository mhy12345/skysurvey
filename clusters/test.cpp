#include <vector>
#include <iostream>
#include <random>
#include "kdtree.h"
using namespace std;
#define PI 3.1415926535

void check_accuracy() {
    srand(0);
    vector<Point> plist;
    KDTree kdt = KDTree();
    int n = 140;
    for (int i=0;i<n;i++) {
        Point pt = Point(random()%10000/10000.0*PI*2, random()%10000/10000.0*PI - PI/2, NULL);
        cout<<"==========="<<i<<"========="<<pt.x<<" "<<pt.y<<endl;
        double res = 0.1;
        for (int j=0;j<plist.size();j++) {
            res = min(res, point_dist(pt, plist[j]));
            //cout<<">>>"<<j<<" "<<res<<endl;
        }
        plist.push_back(pt);
        double res2 = kdt.Search(pt, 0.1).first;
        kdt.Insert(pt);
        //cout<<i<<" "<<res<<" "<<res2<<endl;
        if (abs(res - res2) > 1e-6)
            cout<<"WRONG"<<endl;
    }
}

int main() {
    check_accuracy();
}

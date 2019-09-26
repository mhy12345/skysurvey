#ifndef __POINT_H
#define __POINT_H

#include <algorithm>

class Point {
    static int cluster_total;
    public:
        double x, y;
        int cluster_id;
        const char* tag;

        // Constructers
        Point(double x, double y, const char* tag);
        Point(const Point& p);
        Point();
        void make_cluster();
};

class KDNode {
    public:
        static const double balance_ratio; // KDTree rebuild when size(child) > size(parent) * balance_ratio
        Point p;
        Point box_min, box_max;
        int size;
        KDNode *lch, *rch;
        int direction;
        double midv;
        KDNode(const Point& p, int d);
        bool is_balanced();
        void update_box(const Point& p);
        double box_dist(const Point& p);
        Point* box_corners();
        void update_size();
};

class KDTree {
    public:
        KDNode* root;
        KDNode** imb_node;
        KDTree();
        void insert(KDNode* &node, const Point& p, int d);
        KDNode* build(Point* begin, Point* end);
        void extract(KDNode* now, Point* &cur);
        std::pair<double,Point*> search(KDNode* now, const Point& p, double r);
        void Insert(const Point& p);
        std::pair<double, Point*> Search(const Point& p, double r);
};

double point_dist(const Point& p1, const Point& p2);
#endif

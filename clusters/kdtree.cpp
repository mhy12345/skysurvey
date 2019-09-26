#include "kdtree.h"
#include <cmath>
#include <iostream>
#include <cassert>
#include <exception>
using namespace std;
#define PI 3.1415926535897
#define DIR_X 0
#define DIR_Y 1
#define DIR_UKN -1

bool point_cmp_x(const Point& p1, const Point& p2) {
    return p1.x < p2.x;
}

bool point_cmp_y(const Point& p1, const Point& p2) {
    return p1.y < p2.y;
}

double angular_separation(double lon1, double lat1, double lon2, double lat2) {
    double sdlon = sin(lon2 - lon1);
    double cdlon = cos(lon2 - lon1);
    double slat1 = sin(lat1);
    double slat2 = sin(lat2);
    double clat1 = cos(lat1);
    double clat2 = cos(lat2);

    double num1 = clat2 * sdlon;
    double num2 = clat1 * slat2 - slat1 * clat2 * cdlon;
    double denominator = slat1 * slat2 + clat1 * clat2 * cdlon;
    return atan2(hypot(num1, num2), denominator);
}

double separation_same_x(double x, double y1, double y2) {
    return min(fmod(y1-y2+2*PI, PI), fmod(y2-y1+2*PI, PI));
}

double separation_same_y(double y, double x1, double x2) {
    double dx = min(fmod(x1-x2+2*PI, PI), fmod(x2-x1+2*PI, PI));
    double c = sin(dx/2)*2 * cos(y);
    return acos((2-c*c)/2);
}

double point_dist(const Point& p1, const Point& p2) {
    return angular_separation(p1.x, p1.y, p2.x, p2.y);
}

bool operator == (const Point& p1, const Point& p2) {
    return p1.x == p2.x && p1.y == p2.y;
}

int Point :: cluster_total = 0;

Point :: Point() {
    this->x = this->y = 0;
    this->cluster_id = -1;
    this->tag = NULL;
}

Point :: Point(double x, double y, const char* tag = NULL) {
    this->x = x;
    this->y = y;
    this->tag = tag;
}

Point :: Point(const Point& p) {
    this->x = p.x;
    this->y = p.y;
    this->tag = p.tag;
    this->cluster_id = p.cluster_id;
}

void Point :: make_cluster() {
    this->cluster_id = ++cluster_total;
}

const double KDNode :: balance_ratio = 0.7;

KDNode :: KDNode(const Point& p, int d) : p(p), box_min(p), box_max(p) {
    this->direction = d;
    this->size = 1;
    this->lch = NULL;
    this->rch = NULL;
    this->midv = d == 0 ? p.x : p.y;
}

bool KDNode :: is_balanced() {
    if (this->lch && this->lch->size > this->size * balance_ratio)
        return false;
    if (this->rch && this->rch->size > this->size * balance_ratio)
        return false;
    return true;
}

void KDNode :: update_box(const Point& p) {
    this->box_min.x = min(this->box_min.x, p.x);
    this->box_max.x = max(this->box_max.x, p.x);
    this->box_min.y = min(this->box_min.y, p.y);
    this->box_max.y = max(this->box_max.y, p.y);
}

Point* KDNode :: box_corners() {
    static Point res[4];
    res[0] = box_min;
    res[1] = box_max;
    res[2] = Point(box_min.x, box_max.y);
    res[3] = Point(box_max.x, box_min.y);
    return res;
}

double KDNode :: box_dist(const Point& p) {
    if (p.x >= box_min.x && p.x <= box_max.x && p.y >= box_min.y && p.y <= box_max.y)
        return 0;
    double res = 1e10;
    Point* plist = box_corners();
    for (int i=0;i<4;i++) {
        Point* pp = plist + i;
        if (p.y >= box_min.y && p.y <= box_max.y) {
            res = min(res, separation_same_y(pp->y, p.x, pp->x));
        } else if (p.x >= box_min.x && p.x <= box_max.x) {
            res = min(res, separation_same_x(pp->x, p.y, pp->y));
        } else {
            res = min(res, point_dist(*pp, p));
        }
    }
    return res;
}

void KDNode :: update_size() {
    size = 1;
    if (lch) size += lch->size;
    if (rch) size += rch->size;
}

KDTree :: KDTree() {
    root = NULL;
    imb_node = NULL;
}

void KDTree :: insert(KDNode* &node, const Point& p, int d) {
    if (node == NULL) {
        node = new KDNode(p, d);
	if (!node) throw runtime_error("Cannot alloc memory!");
        return ;
    }
    if (node->direction == DIR_X) {
        if (p.x <= node->midv) {
            //cout<<"LCHX"<<endl;
            insert(node->lch, p, 1-d);
        } else {
            //cout<<"RCHX"<<endl;
            insert(node->rch, p, 1-d);
        }
    } else if (node->direction == DIR_Y) {
        if (p.y <= node->midv) {
            //cout<<"LCHY"<<endl;
            insert(node->lch, p, 1-d);
        } else {
            //cout<<"RCHY"<<endl;
            insert(node->rch, p, 1-d);
        }
    }
    node->update_box(p);
    node->update_size();
    if (!node->is_balanced()) {
        imb_node = &node;
    }
}

KDNode* KDTree :: build(Point* begin, Point* end) {
    if (begin >= end) {
        return NULL;
    }
    Point* cur = begin + (end-begin)/2;
    KDNode* node = new KDNode(*cur, DIR_UKN);
    if (!node) throw runtime_error("Cannot alloc memory!");
    for (Point* it = begin; it != end; it++) {
        node->box_min.x = min(node->box_min.x, it->x);
        node->box_min.y = min(node->box_min.y, it->y);
        node->box_max.x = max(node->box_max.x, it->x);
        node->box_max.y = max(node->box_max.y, it->y);
    }
    if (node->box_max.x - node->box_min.x > node->box_max.y - node->box_min.y) {
        node->direction = DIR_X;
        nth_element(begin, cur, end, point_cmp_x);
        node->p = *cur;
        node->midv = cur->x;
    } else {
        node->direction = DIR_Y;
        nth_element(begin, cur, end, point_cmp_y);
        node->p = *cur;
        node->midv = cur->y;
    }
    node->lch = build(begin, cur);
    node->rch = build(cur+1, end);
    node->update_size();
    return node;
}

void KDTree :: extract(KDNode* now, Point* &cur) {
    if (!now)return;
    *(cur++) = now->p;
    extract(now->lch, cur);
    extract(now->rch, cur);
    delete now;
}

pair<double,Point*> KDTree :: search(KDNode* node, const Point& p, double r) {
    pair<double, Point*> res = make_pair(r, (Point*)NULL);
    if (!node) return res;
    double tr = point_dist(node->p, p);
    res = min(res, make_pair(tr, &(node->p)));
    if (node->lch && node->lch->box_dist(p) <= res.first) {
        res = min(res, search(node->lch, p, res.first));
    }
    if (node->rch && node->rch->box_dist(p) <= res.first) {
        res = min(res, search(node->rch, p, res.first));
    }
    return res;
}

void KDTree :: Insert(const Point& p) {
    imb_node = NULL;
    insert(root, p, DIR_X);
    if (imb_node) {
        static const int maxn = 10000000;
        static Point plist[maxn];
        int s = (*imb_node) -> size;
        Point* top = plist;
        extract(*imb_node, top);
        assert(top - plist == s);
        *imb_node = build(plist, top);
    }
}

pair<double, Point*> KDTree :: Search(const Point& p, double r) {
    return search(root, p, r);
}

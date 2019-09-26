#include <mysql/mysql.h>
#include <iostream>
#include <cstdio>
#include <cerrno>
#include <cstring>
#include <cassert>
#include <cstdlib>
#include "kdtree.h"
#include "config.h"
using namespace std;
#define PI 3.1415926535897
#define CRI ((0.5/3600/180*PI) * 2)
#define DISPLAY_FREQ 1000


int main() {
    MYSQL mysql;
    mysql_init(&mysql);
    printf("Connect...\n");
    if (!mysql_real_connect(&mysql, MYSQL_HOST_IP, MYSQL_USER_NAME, MYSQL_USER_PASSWORD, MYSQL_DATABASE, 3306, NULL, 0)) {
        const char* es;
        es = mysql_error(&mysql);
        printf("connect failed!\n");
        printf("error : %s\n", es);
    }

    printf("Clear table <clusters>...\n");
    //To write data, We need to clear the database first.
    string sql = "drop table clusters;";
    mysql_query(&mysql, sql.c_str());
    sql = "create table clusters(id int not null auto_increment primary key, star_id varchar(60), cluster_id int);";
    mysql_query(&mysql, sql.c_str());

    //Fetch coordinates.
    printf("Fetch coordinates...\n");
    
    sql = "select candidates.id,candidates.RA,candidates.Decl from candidates inner join supernovae on candidates.id=supernovae.id where supernovae.tag='SUPERNOVA';";
    mysql_query(&mysql, sql.c_str());
    MYSQL_RES *m_res;
    MYSQL_ROW m_row;
    m_res = mysql_store_result(&mysql);
    if(m_res==NULL) {
        printf("select username Error \n");
        return 0;
    }
    assert(mysql_num_fields(m_res) == 3);

    KDTree kdt;
    int cnt_stars = 0;
    int cnt_new_stars = 0;
    int row_count = mysql_num_rows(m_res);
    printf("%d rows fetched...\n", row_count);
    while ((m_row = mysql_fetch_row(m_res))) {
        cnt_stars ++;
        if (cnt_stars % DISPLAY_FREQ == 0) {
            printf("PROGRESS %d/%d = %.1f%%   NEW_STARS %d/%d=%.1f%%\n", cnt_stars, row_count, 100.0*cnt_stars/row_count, cnt_new_stars, cnt_stars, 100.0 * cnt_new_stars / cnt_stars);
        }
        double dx = 0, dy = 0;
        char *buf = new char[61];
        sscanf(m_row[1], "%lf", &dx);
        sscanf(m_row[2], "%lf", &dy);
        sscanf(m_row[0], "%s", buf);

        Point pt = Point(dx/180*PI, dy/180*PI, buf);
        pair<double, Point*> res = kdt.Search(pt, 1e10);
        int cluster_id = -1;
        const char* source = NULL;
        if (res.second && res.first < CRI) { 
            cluster_id = res.second->cluster_id;
            source = res.second->tag;
        } else {
            pt.make_cluster();
            cluster_id = pt.cluster_id;
            kdt.Insert(pt);
            source = pt.tag;
            cnt_new_stars ++;
        }
        sql = (string)"INSERT INTO clusters (star_id, cluster_id) values ('"+pt.tag+"','"+to_string(cluster_id)+"')";
        mysql_query(&mysql, sql.c_str());
    }
    mysql_close(&mysql);
}

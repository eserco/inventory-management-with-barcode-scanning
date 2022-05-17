
import sqlite3

conn = sqlite3.connect('stock.db')

c = conn.cursor()

###FIRST ITEM ON ITEMLIST
#inserts into item table
def insert_prod(supp_name,cat_name,item_code,name,uom,size,thickness,date,stock_min_inp):
    with conn:
        c.execute("SELECT total_quantity FROM item WHERE name = :name COLLATE NOCASE OR item_code = :item_code",{'name':name, 'item_code':item_code})
        check = c.fetchone()
    #print(check)
    if check is None:
        print("This item is new.")
        with conn:
            c.execute("INSERT INTO item VALUES (:supp_name, :cat_name, :item_code, :name, :total_cost, :total_quantity, :uom, :size, :thickness, :date_time, :min_stock)",\
                                                {'supp_name':supp_name, 'cat_name': cat_name, 'item_code':item_code, 'name': name,\
                                                'uom':uom, 'size':size, 'thickness':thickness, 'total_cost': 0 , 'total_quantity': 0,\
                                                'date_time':date, 'min_stock':stock_min_inp})
            check = c.fetchone()
            print(check)
        print("A Record with the name %s and item_code %s is created in the item database." % (name,item_code))
    else:
        print("Either the stock name %s or item code %s already defines an stock item record in database." % (name,item_code))
        return check

#deletes a row with the matching name from item table
def del_stock(name):
    with conn:
        c.execute("SELECT * FROM item WHERE name = :name",{'name':name})
        check = c.fetchone()
    if check is None:
        print("No item associated with this %s is found in the item table" % (name))
    else:
        with conn:
            c.execute("DELETE from item WHERE name = :name",{'name': name})
    return check
       
###SECOND ITEM ON ITEMLIST
#inserts into stock table    
def insert_cost(supp_name,name,q,cost,date,supp_item_name):
    with conn:
        c.execute("SELECT total_quantity FROM item WHERE name = :name COLLATE NOCASE",{'name':name})
        check = c.fetchone()
    if check is None:
        print("Stock Item does not exist in the items table")
    else:
        with conn:
            c.execute("INSERT INTO stock VALUES (:supp_name,:name, :quantity, :cost, :date_time, :supp_item_name)",\
                     {'supp_name':supp_name,'name': name, 'quantity': q, 'cost': cost, 'date_time':date,'supp_item_name':supp_item_name})
    return check
    
#reduces the stock count by the given amount in one stock entry selected randomly among many entries 
def update_quantity(name, val):
    with conn:
        c.execute("SELECT quantity,rowid FROM stock WHERE name = :name ORDER BY RANDOM() LIMIT 1;",{'name': name})
        z = c.fetchone()
        if z is None:
            print("This item does not exist in stock table")
        else:
            row_id = z[1]
            quantity = z[0]+val
            print(row_id)
            print(quantity) #('''UPDATE books SET price = ? WHERE id = ?''', (newPrice, book_id))
            c.execute('''UPDATE stock SET quantity = ? WHERE rowid = ?''',(quantity, row_id))
    return z

#deletes all the rows associated with the provided name from the stock table
def remove_stock(name):
    with conn:
        c.execute("SELECT * FROM stock WHERE name = :name",{'name':name})
        check = c.fetchone()
    if check is None:
        print("No item associated with this %s is found in the item table" % (name))
    else:
        with conn:
            c.execute("DELETE from stock WHERE name = :name",
                    {'name': name})
            conn.commit()
    return check
    
#    with conn:
#        c.execute("DELETE from stock WHERE name = :name",
#                  {'name': name})
#        conn.commit()
        
###THIRD ITEM ON VIEWLIST
#show supplier based search results (..[supplier name])
def show_supp(supp_name,func_keyword):
    if func_keyword is None:
        with conn:
            c.execute("SELECT * FROM item WHERE supp_name LIKE ?",('%{}%'.format(supp_name),))
            check = c.fetchall()
    else:
        with conn:
            c.execute("SELECT * FROM item WHERE supp_name LIKE ? AND min_stock > total_quantity",('%{}%'.format(supp_name),))
            check = c.fetchall()
    return check
    
#show category based search results (.[category name])
def show_cat(cat_name,func_keyword):
    if func_keyword is None:
        with conn:
            c.execute("SELECT * FROM item WHERE cat_name LIKE ?",('%{}%'.format(cat_name),))
            check = c.fetchall()
    else:
        with conn:
            c.execute("SELECT * FROM item WHERE cat_name LIKE ? AND min_stock > total_quantity",('%{}%'.format(cat_name),))
            check = c.fetchall()
    return check
    
#show name based search results
def show_stock(name=None,func_keyword=None): 
    if not name and not func_keyword:
        with conn:           
            c.execute("SELECT * FROM item")
    elif name and not func_keyword:
        with conn:           
            c.execute("SELECT * FROM item WHERE name LIKE ?",('%{}%'.format(name),))         
    elif not name and func_keyword:    
        with conn:           
            c.execute("SELECT * FROM item WHERE min_stock > total_quantity")
    elif name and func_keyword:    
        with conn:
            c.execute("SELECT * FROM item WHERE name LIKE ? AND min_stock > total_quantity",('%{}%'.format(name),))          
    return c.fetchall()

#conn.close()
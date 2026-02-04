from app.database import init_db
from app.database.database import SessionLocal
from app.models.student import Student
from app.utils.auth import get_password_hash

def create_default_admin():
    db = SessionLocal()
    try:
        # 检查是否已有管理员账号
        admin = db.query(Student).filter(Student.username == "admin").first()
        if not admin:
            # 创建默认管理员账号
            hashed_password = get_password_hash("admin123")
            admin = Student(
                name="管理员",
                username="admin",
                password_hash=hashed_password,
                is_admin=True,
                phone="12345678900",
                email="admin@example.com",
                department="管理部门"
            )
            db.add(admin)
            db.commit()
            print("默认管理员账号创建成功: username=admin, password=admin123")
        else:
            print("默认管理员账号已存在")
    finally:
        db.close()

if __name__ == "__main__":
    print("初始化数据库...")
    init_db()
    print("数据库初始化完成")
    print("创建默认管理员账号...")
    create_default_admin()
    print("操作完成")

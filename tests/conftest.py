import os
import shutil
import pytest
from repository.database import db
from models.group import Group
from models.payment import Payment
from models.session import GroupSession
from models.debtor_attribute import DebtorAttribute


# @pytest.fixture
@pytest.fixture(scope='function', autouse=True)
def fixture_app():
    # セットアップ処理
    # テスト用のコンフィグを使うために引数にtestingを指定する
    from app import app

    # データベースを利用するための宣言をする
    app.app_context().push()

    # テスト用データベースのテーブルを作成する
    with app.app_context():
        db.create_all()

    # テストを実行する
    yield

    # クリーンナップ処理
    # Groupテーブルのレコードを削除する
    Group.query.delete()

    # Paymentテーブルのレコードを削除する
    Payment.query.delete()

    # GroupSessionテーブルのレコードを削除する
    GroupSession.query.delete()

    # DebtorAttributeテーブルのレコードを削除する
    DebtorAttribute.query.delete()


    db.session.commit()


# Flaskのテストクライアントを返すフィクスチャ関数を作成する
@pytest.fixture
def client(fixture_app):
    # Flaskのテスト用クライアントを返す
    return fixture_app.test_client()

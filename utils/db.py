from typing import Union, List, Any, Optional, TypeVar

from sqlalchemy import select, update, Select, Column, Update, ColumnElement

T = TypeVar("T")


class DB:
    def __init__(self, async_session):
        self.async_session = async_session

    # 增加数据
    async def add(self, table: Union[T | List[T]]) -> T:
        async with self.async_session() as session:
            async with session.begin():
                if isinstance(table, list):
                    session.add_all(table)
                else:
                    session.add(table)
        return table

    # 删除数据
    async def delete(self, table: T, *criteria: ColumnElement[bool]) -> T | List[T]:
        async with self.async_session() as session:
            async with session.begin():
                deleted_records = []
                if criteria:
                    stmt = self.build_query(table, *criteria)
                    if result := (await session.execute(stmt)).scalars().all():
                        [await session.delete(i) for i in result]
                        deleted_records = result
                else:
                    await session.delete(table)
                    deleted_records.append(table)
        if deleted_records:
            return deleted_records if deleted_records[1:] else deleted_records[0]

    # 查询单个数据
    async def get_one(
        self,
        table_or_stmt: T | Select[tuple[Any]] | Select,
        *criteria: ColumnElement[bool],
        joins: Optional[List[Any]] = None,
        order_by: Optional[List[Union[Column, str]]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        options: Optional[List[Any]] = None,
    ) -> T:
        stmt = self.build_query(
            table_or_stmt,
            *criteria,
            joins=joins,
            order_by=order_by,
            offset=offset,
            limit=limit,
            options=options,
        )
        async with self.async_session() as session:
            scalars = (await session.execute(stmt)).scalars()
            return scalars.unique().one_or_none()

    # 查询全部数据
    async def get_all(
        self,
        table_or_stmt: T | Select[tuple[Any]] | Select,
        *criteria: ColumnElement[bool],
        joins: Optional[List[Any]] = None,
        order_by: Optional[List[Union[Column, str]]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        options: Optional[List[Any]] = None,
    ) -> list[T]:
        stmt = self.build_query(
            table_or_stmt,
            *criteria,
            joins=joins,
            order_by=order_by,
            offset=offset,
            limit=limit,
            options=options,
        )
        async with self.async_session() as session:
            return (await session.execute(stmt)).scalars().unique().all()

    # 更新数据
    async def update(
        self,
        table_or_stmt: T | Select[tuple[Any]] | Select | Update,
        *criteria: ColumnElement[bool],
        **values: Any,
    ) -> T | None:
        async with self.async_session() as session:
            async with session.begin():
                if isinstance(table_or_stmt, type):
                    # 如果是一个模型类
                    stmt = update(table_or_stmt).where(*criteria).values(**values)
                    await session.execute(stmt)

                    select_stmt = select(table_or_stmt).where(*criteria)
                    result = await session.execute(select_stmt)
                    updated_row = result.scalar_one_or_none()
                elif isinstance(table_or_stmt, (Select, Update)):
                    result = await session.execute(table_or_stmt)
                    if isinstance(table_or_stmt, Update):
                        select_stmt = select(table_or_stmt.table).where(*criteria)
                        result = await session.execute(select_stmt)
                    updated_row = result.scalar_one_or_none()
                else:
                    raise ValueError("Unsupported statement type")

                await session.commit()
                return updated_row

    # 过滤数据
    async def filter(
        self,
        table_or_stmt: T | Select[tuple[Any]] | Select,
        *criteria: ColumnElement[bool],
        joins: Optional[List[Any]] = None,
        order_by: Optional[List[Union[Column, str]]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        options: Optional[List[Any]] = None,
    ) -> list[T]:
        stmt = self.build_query(
            table_or_stmt,
            *criteria,
            joins=joins,
            order_by=order_by,
            offset=offset,
            limit=limit,
            options=options,
        )
        async with self.async_session() as session:
            return (await session.execute(stmt)).scalars().all()

    async def close(self):
        async with self.async_session() as session:
            await session.close()

    @staticmethod
    def build_query(
        table_or_stmt: T | Select[tuple[Any]] | Select,
        *criteria: ColumnElement[bool],
        joins: Optional[List[Any]] = None,
        order_by: Optional[List[Union[Column, str]]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        options: Optional[List[Any]] = None,
    ):
        if not isinstance(table_or_stmt, (Select, Select[tuple[Any]])):
            table_or_stmt = select(table_or_stmt)
        if criteria:
            table_or_stmt = table_or_stmt.where(*criteria)
        if joins:
            for j in joins:
                table_or_stmt = table_or_stmt.join(j)
        if order_by:
            table_or_stmt = table_or_stmt.order_by(*order_by)
        if offset:
            table_or_stmt = table_or_stmt.offset(offset)
        if limit:
            table_or_stmt = table_or_stmt.limit(limit)
        if options:
            table_or_stmt = table_or_stmt.options(*options)
        return table_or_stmt

import React, { useState, useEffect } from "react";
import { IData } from "../schemas/IData";

interface IProps {
  data: IData[] | any;
}

const TableComponent: React.FC<IProps> = ({ data }) => {
  const [tableId, setTableId] = useState<string>("");
  const [notifications, setNotifications] = useState<
    { message: string; type: "warning" | "error" }[]
  >([]);
  const [filteredData, setFilteredData] = useState<IData[]>([]);
  const pluralize = (count: number, one: string, two: string, five: string) => {
    if (count === 1) {
      return one;
    } else if (count >= 2 && count <= 4) {
      return two;
    } else {
      return five;
    }
  };
  useEffect(() => {
    if (data && data.length > 0) {
      setTableId(data[0].tabel_id);
      const newNotifications: { message: string; type: "warning" | "error" }[] =
        [];
      const newData = data.filter((item: IData) => {
        if (item.remaining_days <= 0) {
          const days = Math.abs(item.remaining_days);
          newNotifications.push({
            message: `Просрочка у Табельный номер: ${item.tabel_id},  ФИО: ${
              item.person_full_name
            } на ${days} ${pluralize(days, "день", "дня", "дней")}!`,
            type: "error",
          });
          return false;
        } else if (item.remaining_days < 3) {
          newNotifications.push({
            message: `Уведомление: Табельный номер: ${item.tabel_id}, ФИО: ${
              item.person_full_name
            } (${item.clothes_name}) - осталось ${
              item.remaining_days
            } ${pluralize(item.remaining_days, "день", "дня", "дней")}`,
            type: "warning",
          });
        }
        return true;
      });
      setNotifications(newNotifications);
      setFilteredData(newData);
    }
  }, [data]);

  if (!filteredData || filteredData.length === 0) {
    return <div className="text-center text-gray-500">Нет данных</div>;
  }

  return (
    <div className="overflow-x-auto">
      <div className="mb-4">
        {notifications.map((notification, index) => (
          <div
            key={index}
            className={`p-4 mb-4 text-white ${
              notification.type === "warning" ? "bg-yellow-500" : "bg-red-500"
            } rounded-md`}>
            {notification.message}
          </div>
        ))}
      </div>
      <table className="w-full border-collapse">
        <thead className="bg-gray-200">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Табельный номер
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              ФИО
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Категория
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Название одежды
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Оставшиеся дни
            </th>
          </tr>
        </thead>
        <tbody>
          {filteredData.map((item: IData, index: number) => (
            <tr
              key={index}
              className={`${
                index % 2 === 0 ? "bg-gray-100" : "bg-white"
              } border-b border-gray-200`}>
              <td className="px-6 py-4 whitespace-nowrap">{item.tabel_id}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                {item.person_full_name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {item.clothes_category}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {item.clothes_name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {item.remaining_days}{" "}
                {pluralize(item.remaining_days, "день", "дня", "дней")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TableComponent;

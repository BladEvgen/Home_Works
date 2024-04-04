import React, { useState, useEffect } from "react";
import { IData } from "../schemas/IData";
import TableComponent from "../components/TableComponent";

const MainPage = () => {
  const [data, setData] = useState<IData[] | any>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/messages/");
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        const responseData = await response.json();
        setData(responseData);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <>
      <div className="container mx-auto p-4">
        <TableComponent data={data} />
      </div>
    </>
  );
};

export default MainPage;

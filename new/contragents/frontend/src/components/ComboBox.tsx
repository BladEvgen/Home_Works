import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import { useEffect, useState } from "react";
import axios from "axios";
import { isDebug } from "../../constants.tsx";

interface IAgent {
  bin: string;
  id: number;
  title: string;
}

export default function ComboBox() {
  const [data, setData] = useState<IAgent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const getData = async () => {
    setIsLoading(true);
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/agents/");
      console.log("Response from API/agents", res.data.data);
      setData(res.data.data);
    } catch (error) {
      if (isDebug) {
        console.error(error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    getData();
  }, []);

  const newData: string[] = data.map((d) => d.title.toString());

  return (
    <>
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <Autocomplete
          disablePortal
          id="combo-box-demo"
          options={newData}
          sx={{ width: 300 }}
          renderInput={(params) => <TextField {...params} label="Agents" />}
        />
      )}
    </>
  );
}

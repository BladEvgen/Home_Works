import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import { useEffect, useState } from "react";
import axios from "axios";
import { isDebug, apiUrl } from "../../apiConfig";

interface IAgent {
  bin: string;
  id: number;
  title: string;
}

interface IComboBoxProps {
  onAgentSelect: (agentId: number | null) => void;
  width?: string;
}

const ComboBox: React.FC<IComboBoxProps> = ({
  onAgentSelect,
  width = "200px",
}) => {
  const [data, setData] = useState<IAgent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const getData = async () => {
    setIsLoading(true);
    try {
      const res = await axios.get(`${apiUrl}/api/agents/`);
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

  const handleAgentSelect = (agent: IAgent | null) => {
    if (agent) {
      onAgentSelect(agent.id);
    } else {
      onAgentSelect(null);
    }
  };

  return (
    <>
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <Autocomplete
          disablePortal
          id="combo-box-demo"
          options={data}
          getOptionLabel={(option: IAgent) => option.title}
          onChange={(event, value) => handleAgentSelect(value)}
          renderInput={(params) => (
            <TextField {...params} label="Agents" sx={{ width }} />
          )}
        />
      )}
    </>
  );
};

export default ComboBox;

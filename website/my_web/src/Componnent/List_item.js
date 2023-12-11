import { React } from "react";
import { BsCheckLg } from "react-icons/bs";
import { AiFillFileText } from "react-icons/ai";
import { Link } from "react-router-dom";
function ItemList({ itemList }) {
  if (itemList == null) {
    return <div></div>;
  }
  let varList = [];
  for (let i in itemList) {
    let cond = true;
    if (varList.length === 0) {
      varList.push(itemList[i]);
    } else {
      for (let j in varList) {
        if (
          (itemList[i][1] === varList[j][0] &&
            itemList[i][0] === varList[j][1]) ||
          (itemList[i][0] === varList[j][0] && itemList[i][1] === varList[j][1])
        ) {
          cond = false;
        }
      }
      if (cond) {
        varList.push(itemList[i]);
      }
    }
  }
  function fillSpan(item) {
    let rel = "";
    if (item[2].includes("Connection")) {
      rel = <strong>{item[2]}</strong>;
    } else {
      rel = <strong>Overlaps</strong>;
    }
    return (
      <span className="name">
        {item[0]} {rel} {item[1]}
      </span>
    );
  }

  const listItems = varList.map((item) => (
    <li key={item} className="rows">
      <AiFillFileText style={{ fontSize: "30px" }} />
      <div className="content">
        <div className="detail" style={{ overflow_y: "scroll" }}>
          <span className="name">{fillSpan(item)}</span>
        </div>
      </div>
      <div hidden={true} id="check">
        <BsCheckLg style={{ fontSize: "30px", color: "green" }} />
      </div>
      <Link to="/rules" state={{ from: item }}>
        {" "}
        CLick me{" "}
      </Link>
    </li>
  ));

  return (
    <div>
      <ul id="span-list">{listItems}</ul>
      <button
        style={{ position: "absolute", color: "red" }}
        onClick={() => {
          sessionStorage.setItem("rules", null);
          window.location.reload(false);
        }}
      >
        Clear
      </button>
    </div>
  );
}
export default ItemList;

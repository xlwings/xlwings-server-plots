import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xlwings as xw
from fastapi import APIRouter, Body, Security

from ..core.auth import User, authenticate

# Require authentication for all endpoints for this router
router = APIRouter(
    dependencies=[Security(authenticate)],
    prefix="/timeseries",
    tags=["Timeseries"],
)


@router.post("/random-walk")
async def random_walk(data: dict = Body):
    with xw.Book(json=data) as book:
        sheet = book.sheets[0]

        # pandas DataFrame with a random walk
        df = pd.DataFrame(
            data=np.random.randn(500),
            index=pd.date_range("1/1/2022", periods=500),
            columns=["Time Series"],
        )
        df["Time Series"] = df["Time Series"].cumsum()
        window = sheet["F1"].value
        df[f"{window}d average"] = df["Time Series"].rolling(window).mean()
        sheet["A1"].expand().clear_contents()
        sheet["A1"].value = df

        # Matplotlib plot
        plt.style.use("fivethirtyeight")
        ax = df.plot(figsize=(12, 8))
        sheet.pictures.add(
            image=ax.get_figure(),
            name="time_series",
            anchor=sheet["E9"],
            export_options={"bbox_inches": "tight", "dpi": 80},
            update=True,
        )

        return book.json()
